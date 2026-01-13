"""Command-line interface for RTSP Scanner"""

import argparse
import concurrent.futures
import sys
from pathlib import Path

from rtsp_scanner.core.port_scanner import PortScanner
from rtsp_scanner.core.rtsp_tester import RTSPTester
from rtsp_scanner.core.channel_scanner import ChannelScanner
from rtsp_scanner.core.camera_checker import CameraChecker
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

  # Scan with credentials and verify they work
  rtsp-network-scanner scan 192.168.1.100 -u admin -p password

  # Check if cameras are actually working (uses ffmpeg)
  rtsp-network-scanner scan 192.168.1.0/24 --check

  # Simple output (less details)
  rtsp-network-scanner scan --simple

  # Detailed output (all info including ffmpeg check)
  rtsp-network-scanner scan --check --detailed
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
    scan.add_argument('--username', '-u', help='Username for authentication')
    scan.add_argument('--password', '-p', help='Password for authentication')
    scan.add_argument('--skip-channels', action='store_true', help='Skip channel discovery')
    scan.add_argument('--check', action='store_true', help='Check if cameras are working (requires ffmpeg)')
    scan.add_argument('--simple', action='store_true', help='Simple output (host, port, status)')
    scan.add_argument('--detailed', action='store_true', help='Detailed output (all available info)')

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

            # Check ffmpeg availability if --check is used
            camera_checker = None
            if args.check:
                camera_checker = CameraChecker(timeout=args.timeout * 3, logger=logger)
                if not camera_checker.is_ffmpeg_available():
                    print("Warning: ffmpeg/ffprobe not found. Install ffmpeg for --check feature.")
                    print("Continuing without camera health check...\n")
                    camera_checker = None

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
                    if not args.simple:
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
                    tester = RTSPTester(timeout=args.timeout, logger=logger)

                    all_channels = []
                    rtsp_hosts = []
                    non_rtsp_hosts = []

                    # Build list of all host:port combinations
                    host_port_list = []
                    for host, ports in open_hosts.items():
                        for port in ports:
                            host_port_list.append((host, port))

                    # Check RTSP protocol in parallel
                    print(f"Checking RTSP protocol on {len(host_port_list)} host(s)...")

                    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
                        future_to_host = {
                            executor.submit(tester.check_rtsp_protocol, host, port): (host, port)
                            for host, port in host_port_list
                        }
                        for future in concurrent.futures.as_completed(future_to_host):
                            host, port = future_to_host[future]
                            protocol_check = future.result()
                            if protocol_check.get('is_rtsp'):
                                rtsp_hosts.append((
                                    host,
                                    port,
                                    protocol_check.get('server_info'),
                                    protocol_check.get('manufacturer')
                                ))
                            else:
                                non_rtsp_hosts.append((host, port))

                    # Report results with manufacturer breakdown
                    if rtsp_hosts:
                        manufacturers = {}
                        for host, port, server_info, manufacturer in rtsp_hosts:
                            mfr = manufacturer or 'Unknown'
                            manufacturers[mfr] = manufacturers.get(mfr, 0) + 1

                        mfr_summary = ', '.join([f"{count} {name}" for name, count in manufacturers.items()])
                        print(f"Found {len(rtsp_hosts)} RTSP host(s): {mfr_summary}")
                    if non_rtsp_hosts:
                        print(f"Skipping {len(non_rtsp_hosts)} non-RTSP host(s)")

                    # Scan only RTSP hosts
                    for host, port, server_info, manufacturer in rtsp_hosts:
                        if manufacturer:
                            logger.info(f"RTSP detected on {host}:{port} ({manufacturer})")
                        elif server_info:
                            logger.info(f"RTSP detected on {host}:{port} ({server_info})")
                        channels = channel_scanner.scan_channels(
                            host,
                            port,
                            args.username,
                            args.password,
                            show_progress=not args.debug
                        )

                        # Add host, port, and manufacturer info to results
                        for channel in channels:
                            channel['host'] = host
                            channel['port'] = port
                            channel['manufacturer'] = manufacturer
                            all_channels.append(channel)

                    # Display channel results
                    if all_channels:
                        # Summarize channel statuses
                        ok_channels = [c for c in all_channels if c.get('status') == 'ok']
                        auth_error_channels = [c for c in all_channels if c.get('status') == 'auth_error']

                        # Show credential validation status
                        if args.username and args.password:
                            if ok_channels:
                                first_valid = ok_channels[0]
                                print(f"\n✓ Credentials VALID ({len(ok_channels)} channel(s) accessible)")
                                if not args.simple:
                                    if first_valid.get('codec'):
                                        print(f"  Codec: {first_valid['codec']}")
                                    if first_valid.get('resolution'):
                                        print(f"  Resolution: {first_valid['resolution']}")
                                print()
                            elif auth_error_channels:
                                print(f"\n✗ Credentials INVALID ({len(auth_error_channels)} channel(s) require auth)")
                                print()
                        else:
                            # No credentials provided - show what was found
                            if ok_channels:
                                print(f"\n✓ {len(ok_channels)} channel(s) accessible without auth")
                            if auth_error_channels:
                                print(f"✗ {len(auth_error_channels)} channel(s) require authentication")
                            if ok_channels or auth_error_channels:
                                print()

                        # Step 3: Check camera health with ffmpeg if requested
                        if camera_checker and all_channels:
                            print("Checking camera health with ffmpeg...")
                            accessible_channels = [c for c in all_channels if c.get('status_code') == 200]

                            if accessible_channels:
                                checked_count = [0]
                                total = len(accessible_channels)

                                def progress_callback(checked, total):
                                    checked_count[0] = checked
                                    if not args.debug:
                                        print(f"\r  Checked {checked}/{total} streams", end='', flush=True)

                                check_results = camera_checker.batch_check(
                                    accessible_channels,
                                    args.username,
                                    args.password,
                                    max_workers=min(5, args.workers),
                                    progress_callback=progress_callback
                                )

                                if not args.debug:
                                    print()  # New line after progress

                                # Update channels with check results
                                check_map = {r.get('url') or f"rtsp://{r.get('host')}:{r.get('port')}{r.get('path')}": r
                                             for r in check_results}

                                working_count = 0
                                for channel in all_channels:
                                    url = channel.get('url') or f"rtsp://{channel.get('host')}:{channel.get('port')}{channel.get('path')}"
                                    if url in check_map:
                                        check = check_map[url]
                                        channel['working'] = check.get('working', False)
                                        channel['check_error'] = check.get('error')
                                        if check.get('working'):
                                            working_count += 1
                                            # Update with ffmpeg-detected values (more accurate)
                                            if check.get('codec'):
                                                channel['codec'] = check['codec']
                                            if check.get('resolution'):
                                                channel['resolution'] = check['resolution']
                                            if check.get('fps'):
                                                channel['fps'] = check['fps']
                                            if check.get('bitrate'):
                                                channel['bitrate'] = check['bitrate']

                                print(f"  {working_count}/{len(accessible_channels)} stream(s) working\n")
                            else:
                                print("  No accessible streams to check\n")

                        # Display results based on output mode
                        print(formatter.format_summary(all_channels, 'Channels'))

                        # Build columns based on output mode
                        if args.simple:
                            # Simple output: minimal info
                            columns = ['host', 'port']
                            if any(c.get('manufacturer') for c in all_channels):
                                columns.append('manufacturer')
                            columns.append('path')
                            columns.append('status')
                            if args.check:
                                columns.append('working')
                        elif args.detailed:
                            # Detailed output: all available info
                            columns = ['host', 'port']
                            if any(c.get('manufacturer') for c in all_channels):
                                columns.append('manufacturer')
                            columns.extend(['path', 'stream_type', 'status'])
                            if any(c.get('codec') for c in all_channels):
                                columns.extend(['codec', 'resolution'])
                            if args.check:
                                columns.append('working')
                                if any(c.get('fps') for c in all_channels):
                                    columns.append('fps')
                                if any(c.get('bitrate') for c in all_channels):
                                    columns.append('bitrate')
                            columns.append('response_time')
                        else:
                            # Default output: balanced info
                            has_codec = any(c.get('codec') for c in all_channels)
                            has_manufacturer = any(c.get('manufacturer') for c in all_channels)

                            if has_codec:
                                if has_manufacturer:
                                    columns = ['host', 'port', 'manufacturer', 'path', 'stream_type', 'status', 'codec', 'resolution']
                                else:
                                    columns = ['host', 'port', 'path', 'stream_type', 'status', 'codec', 'resolution']
                            else:
                                if has_manufacturer:
                                    columns = ['host', 'port', 'manufacturer', 'path', 'stream_type', 'status']
                                else:
                                    columns = ['host', 'port', 'path', 'stream_type', 'status']

                            if args.check:
                                columns.append('working')
                            columns.append('response_time')

                        print(formatter.format_table(all_channels, columns))
                        results = all_channels
                    elif rtsp_hosts:
                        print("\nNo accessible channels found on RTSP hosts")
                        results = port_results
                    elif non_rtsp_hosts:
                        print(f"\nNo RTSP protocol detected on any of the {len(non_rtsp_hosts)} open port(s)")
                        print("These may be HTTP cameras or other services")
                        results = port_results
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
