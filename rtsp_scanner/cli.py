"""Command-line interface for RTSP Scanner"""

import argparse
import sys
from pathlib import Path

from rtsp_scanner.core.port_scanner import PortScanner
from rtsp_scanner.core.rtsp_tester import RTSPTester
from rtsp_scanner.core.channel_scanner import ChannelScanner
from rtsp_scanner.utils.logger import setup_logger
from rtsp_scanner.utils.output import OutputFormatter
from rtsp_scanner.utils.network import get_local_network, get_local_ip


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Network RTSP stream scanner and debugger',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan local network (auto-detected)
  rtsp-network-scanner scan

  # Scan specific network
  rtsp-network-scanner scan 192.168.1.0/24

  # Scan single host
  rtsp-network-scanner scan 192.168.1.100
        """
    )

    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--log-file', type=str, help='Log to file')
    parser.add_argument('--output', '-o', type=str, help='Output file (JSON or CSV)')
    parser.add_argument('--timeout', type=float, default=2.0, help='Connection timeout (default: 2.0s)')
    parser.add_argument('--workers', type=int, default=50, help='Max concurrent workers (default: 50)')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Main scan command - does everything
    scan = subparsers.add_parser('scan', help='Scan for RTSP cameras (ports + channels)')
    scan.add_argument('target', nargs='?', help='Network (CIDR), IP range, or single host (auto-detected if omitted)')
    scan.add_argument('--ports', nargs='+', type=int, help='Ports to scan')
    scan.add_argument('--username', '-u', help='Username for channel scan')
    scan.add_argument('--password', '-p', help='Password for channel scan')
    scan.add_argument('--skip-channels', action='store_true', help='Skip channel discovery')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Setup logger
    logger = setup_logger(debug=args.debug, log_file=args.log_file)
    formatter = OutputFormatter()

    try:
        results = []

        # Execute command
        if args.command == 'scan':
            # Determine target
            target = args.target
            if target is None:
                # Auto-detect network
                target = get_local_network()
                local_ip = get_local_ip()
                print(f"Auto-detected network: {target} (Your IP: {local_ip})")

            # Step 1: Scan for open RTSP ports
            print(f"Scanning {target}...\n")
            port_scanner = PortScanner(timeout=args.timeout, max_workers=args.workers, logger=logger)

            # Determine if it's a network, range, or single host
            show_progress = not args.debug
            if '/' in target:
                # CIDR network
                port_results = port_scanner.scan_network(target, ports=args.ports, show_progress=show_progress)
            elif '-' in target:
                # IP range (e.g., 192.168.1.1-192.168.1.254)
                parts = target.split('-')
                port_results = port_scanner.scan_ip_range(parts[0].strip(), parts[1].strip(), ports=args.ports, show_progress=show_progress)
            else:
                # Single host
                port_results = port_scanner.scan_host(target, ports=args.ports, show_progress=show_progress)

            # Display port scan results
            if port_results:
                open_results = [r for r in port_results if r.get('status') == 'open']
                if open_results:
                    print(formatter.format_summary(open_results, "Ports"))
                    print(formatter.format_table(open_results, ['host', 'port', 'response_time']))

            # Step 2: Scan for channels on hosts with open ports
            if not args.skip_channels and port_results:
                open_hosts = {}
                for result in port_results:
                    if result.get('status') == 'open':
                        host = result['host']
                        port = result['port']
                        if host not in open_hosts:
                            open_hosts[host] = []
                        open_hosts[host].append(port)

                if open_hosts:
                    print()  # Empty line for spacing
                    channel_scanner = ChannelScanner(timeout=args.timeout, max_workers=args.workers, logger=logger)

                    all_channels = []
                    for host, ports in open_hosts.items():
                        for port in ports:
                            channels = channel_scanner.scan_channels(
                                host,
                                port,
                                args.username,
                                args.password,
                                show_progress=not args.debug
                            )

                            # Add host and port info to results
                            for channel in channels:
                                channel['host'] = host
                                channel['port'] = port
                                all_channels.append(channel)

                    # Display channel results
                    if all_channels:
                        # Show credential validation status if credentials were provided
                        if args.username and args.password:
                            valid_channels = [c for c in all_channels if c.get('status_code') == 200]
                            if valid_channels:
                                first_valid = valid_channels[0]
                                print(f"\n✓ Credentials VALID")
                                if first_valid.get('codec'):
                                    print(f"  Codec: {first_valid['codec']}")
                                if first_valid.get('resolution'):
                                    print(f"  Resolution: {first_valid['resolution']}")
                                print()
                            else:
                                # Check if all channels require auth (invalid credentials)
                                auth_required = [c for c in all_channels if c.get('status_code') == 401]
                                if auth_required:
                                    print(f"\n✗ Credentials INVALID")
                                    print()

                        print(formatter.format_summary(all_channels, 'Channels'))

                        # Only show codec/resolution if at least one channel has codec data
                        has_codec = any(c.get('codec') for c in all_channels)
                        if has_codec:
                            print(formatter.format_table(all_channels, ['host', 'port', 'path', 'stream_type', 'codec', 'resolution', 'response_time']))
                        else:
                            print(formatter.format_table(all_channels, ['host', 'port', 'path', 'stream_type', 'response_time']))
                        results = all_channels
                    else:
                        print("\nNo accessible channels found")
                        results = port_results
                else:
                    print("\nNo open RTSP ports found")
                    results = port_results
            else:
                results = port_results

        # Export results
        if args.output and results:
            output_path = Path(args.output)
            if output_path.suffix.lower() == '.json':
                formatter.export_json(results, args.output)
                print(f"\nExported to {args.output}")
            elif output_path.suffix.lower() == '.csv':
                formatter.export_csv(results, args.output)
                print(f"\nExported to {args.output}")

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted")
        return 130
    except Exception as e:
        print(f"\nError: {str(e)}")
        if args.debug:
            raise
        return 1


if __name__ == '__main__':
    sys.exit(main())
