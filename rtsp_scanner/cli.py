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
  # Auto-scan local network
  rtsp-network-scanner network

  # Scan specific network
  rtsp-network-scanner network 192.168.1.0/24

  # Scan single host
  rtsp-network-scanner ports 192.168.1.100

  # Test RTSP URL
  rtsp-network-scanner test rtsp://192.168.1.100:554/stream

  # Quick channel scan
  rtsp-network-scanner quick 192.168.1.100
        """
    )

    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--log-file', type=str, help='Log to file')
    parser.add_argument('--output', '-o', type=str, help='Output file (JSON or CSV)')
    parser.add_argument('--timeout', type=float, default=2.0, help='Connection timeout (default: 2.0s)')
    parser.add_argument('--workers', type=int, default=50, help='Max concurrent workers (default: 50)')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Network scan command
    scan_net = subparsers.add_parser('network', help='Scan network for RTSP ports')
    scan_net.add_argument('network', nargs='?', help='Network in CIDR notation (auto-detected if omitted)')
    scan_net.add_argument('--ports', nargs='+', type=int, help='Ports to scan')

    # Scan ports command
    scan_ports = subparsers.add_parser('ports', help='Scan ports on single host')
    scan_ports.add_argument('host', help='Target host IP or hostname')
    scan_ports.add_argument('--ports', nargs='+', type=int, help='Ports to scan')

    # Scan IP range command  
    scan_range = subparsers.add_parser('range', help='Scan IP range')
    scan_range.add_argument('start_ip', help='Starting IP')
    scan_range.add_argument('end_ip', help='Ending IP')
    scan_range.add_argument('--ports', nargs='+', type=int, help='Ports to scan')

    # Test URL command
    test_url = subparsers.add_parser('test', help='Test RTSP URL')
    test_url.add_argument('url', help='RTSP URL')
    test_url.add_argument('--username', '-u', help='Username')
    test_url.add_argument('--password', '-p', help='Password')

    # Validate URL command
    validate = subparsers.add_parser('validate', help='Validate RTSP URL')
    validate.add_argument('url', help='RTSP URL')

    # Scan channels command
    scan_ch = subparsers.add_parser('channels', help='Scan for channels')
    scan_ch.add_argument('host', help='Target host')
    scan_ch.add_argument('--port', type=int, default=554, help='Port (default: 554)')
    scan_ch.add_argument('--username', '-u', help='Username')
    scan_ch.add_argument('--password', '-p', help='Password')
    scan_ch.add_argument('--paths', nargs='+', help='Custom paths')
    scan_ch.add_argument('--with-creds', action='store_true', help='Try common credentials')

    # Quick scan command
    quick = subparsers.add_parser('quick', help='Quick scan')
    quick.add_argument('host', help='Target host')
    quick.add_argument('--port', type=int, default=554, help='Port (default: 554)')

    # Numbered channels command
    numbered = subparsers.add_parser('numbered', help='Scan numbered channels')
    numbered.add_argument('host', help='Target host')
    numbered.add_argument('--port', type=int, default=554, help='Port (default: 554)')
    numbered.add_argument('--range', type=str, default='1-16', help='Range (default: 1-16)')
    numbered.add_argument('--username', '-u', help='Username')
    numbered.add_argument('--password', '-p', help='Password')

    # Test credentials command
    test_creds = subparsers.add_parser('credentials', help='Test credentials')
    test_creds.add_argument('url', help='RTSP URL')

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
        if args.command == 'network':
            # Auto-detect network if not provided
            if args.network is None:
                network = get_local_network()
                local_ip = get_local_ip()
                logger.info(f"Auto-detected: {network} (Your IP: {local_ip})")
            else:
                network = args.network

            scanner = PortScanner(timeout=args.timeout, max_workers=args.workers, logger=logger)
            results = scanner.scan_network(network, ports=args.ports)
            print(formatter.format_summary(results, "Network Scan"))
            if results:
                print(formatter.format_table(results, ['host', 'port', 'status', 'response_time']))

        elif args.command == 'ports':
            scanner = PortScanner(timeout=args.timeout, max_workers=args.workers, logger=logger)
            results = scanner.scan_host(args.host, ports=args.ports)
            print(formatter.format_summary(results, "Port Scan"))
            if results:
                print(formatter.format_table(results, ['host', 'port', 'status', 'response_time']))

        elif args.command == 'range':
            scanner = PortScanner(timeout=args.timeout, max_workers=args.workers, logger=logger)
            results = scanner.scan_ip_range(args.start_ip, args.end_ip, ports=args.ports)
            print(formatter.format_summary(results, "IP Range Scan"))
            if results:
                print(formatter.format_table(results, ['host', 'port', 'status', 'response_time']))

        elif args.command == 'test':
            tester = RTSPTester(timeout=args.timeout, logger=logger)
            if args.username and args.password:
                result = tester.test_rtsp_with_auth(args.url, args.username, args.password)
            else:
                result = tester.test_rtsp_connection(args.url)

            results = [result]
            print(formatter.format_summary(results, "URL Test"))
            print(formatter.format_json(result, pretty=True))

        elif args.command == 'validate':
            tester = RTSPTester(logger=logger)
            is_valid, message = tester.validate_rtsp_url(args.url)
            print(f"\nURL: {args.url}")
            print(f"Valid: {is_valid}")
            print(f"Message: {message}\n")

            if is_valid:
                parsed = tester.parse_rtsp_url(args.url)
                print("Parsed:")
                print(formatter.format_json(parsed, pretty=True))

        elif args.command == 'channels':
            scanner = ChannelScanner(timeout=args.timeout, max_workers=args.workers, logger=logger)

            if args.with_creds:
                results = scanner.scan_with_credentials(args.host, args.port, custom_paths=args.paths)
            else:
                results = scanner.scan_channels(args.host, args.port, args.username, args.password, args.paths)

            print(formatter.format_summary(results, "Channel Scan"))
            if results:
                headers = ['path', 'status_code', 'response_time', 'requires_auth']
                if args.with_creds and results and 'username' in results[0]:
                    headers.extend(['username', 'password'])
                print(formatter.format_table(results, headers))

        elif args.command == 'quick':
            scanner = ChannelScanner(timeout=args.timeout, max_workers=args.workers, logger=logger)
            results = scanner.quick_scan(args.host, args.port)
            print(formatter.format_summary(results, "Quick Scan"))
            if results:
                print(formatter.format_table(results, ['path', 'status_code', 'response_time']))

        elif args.command == 'numbered':
            scanner = ChannelScanner(timeout=args.timeout, max_workers=args.workers, logger=logger)

            # Parse range
            if '-' in args.range:
                start, end = map(int, args.range.split('-'))
                channel_range = range(start, end + 1)
            else:
                channel_range = range(1, 17)

            results = scanner.scan_numbered_channels(args.host, args.port, channel_range, args.username, args.password)
            print(formatter.format_summary(results, "Numbered Scan"))
            if results:
                print(formatter.format_table(results, ['path', 'status_code', 'response_time']))

        elif args.command == 'credentials':
            tester = RTSPTester(timeout=args.timeout, logger=logger)
            results = tester.test_common_credentials(args.url)
            print(formatter.format_summary(results, "Credential Test"))

            if results:
                print("\nWorking credentials:")
                for item in results:
                    print(f"  User: {item['username']}, Pass: {item['password']}")
            else:
                print("\nNo credentials found")

        # Export results
        if args.output and results:
            output_path = Path(args.output)
            if output_path.suffix.lower() == '.json':
                formatter.export_json(results, args.output)
                logger.info(f"Exported to {args.output}")
            elif output_path.suffix.lower() == '.csv':
                formatter.export_csv(results, args.output)
                logger.info(f"Exported to {args.output}")

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted")
        return 130
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.debug:
            raise
        return 1


if __name__ == '__main__':
    sys.exit(main())
