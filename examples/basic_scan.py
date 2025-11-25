#!/usr/bin/env python3
"""
Basic RTSP Scanner Example

This example demonstrates how to use RTSP Scanner as a Python library
to scan a network for RTSP cameras and test their channels.
"""

from rtsp_scanner.core.port_scanner import PortScanner
from rtsp_scanner.core.rtsp_tester import RTSPTester
from rtsp_scanner.core.channel_scanner import ChannelScanner
from rtsp_scanner.utils.logger import setup_logger
from rtsp_scanner.utils.output import OutputFormatter


def main():
    """Main example function"""

    # Setup logger with debug mode
    logger = setup_logger(debug=True, log_file='scan.log')
    formatter = OutputFormatter()

    print("=" * 70)
    print("RTSP Scanner - Basic Example")
    print("=" * 70)

    # Example 1: Scan a single host for open RTSP ports
    print("\n1. Scanning host for open RTSP ports...")
    print("-" * 70)

    scanner = PortScanner(timeout=2.0, max_workers=10, logger=logger)
    host = '192.168.1.100'  # Change this to your camera IP

    # show_progress=False to disable progress bar (useful when debug=True)
    port_results = scanner.scan_host(host, show_progress=False)

    if port_results:
        print(f"\nFound {len(port_results)} open port(s):")
        print(formatter.format_table(port_results, ['host', 'port', 'status', 'response_time']))
    else:
        print(f"\nNo open RTSP ports found on {host}")

    # Example 2: Test a specific RTSP URL
    print("\n2. Testing RTSP URL...")
    print("-" * 70)

    tester = RTSPTester(timeout=5.0, logger=logger)
    test_url = 'rtsp://192.168.1.100:554/stream'  # Change this to your RTSP URL

    # Validate URL format
    is_valid, message = tester.validate_rtsp_url(test_url)
    print(f"\nURL Validation: {message}")

    if is_valid:
        # Test connection
        result = tester.test_rtsp_connection(test_url)
        print(f"\nConnection Result:")
        print(formatter.format_json(result, pretty=True))

    # Example 3: Scan for available channels
    print("\n3. Quick channel scan...")
    print("-" * 70)

    channel_scanner = ChannelScanner(timeout=5.0, max_workers=10, logger=logger)

    # Quick scan with most common paths
    # show_progress=False to disable progress bar (useful when debug=True)
    channels = channel_scanner.quick_scan(host, show_progress=False)

    if channels:
        print(f"\nFound {len(channels)} available channel(s):")
        print(formatter.format_table(
            channels,
            ['path', 'status_code', 'response_time', 'requires_auth']
        ))
    else:
        print(f"\nNo channels found on {host}")

    # Example 4: Test common credentials (if channels require auth)
    if channels and any(ch.get('requires_auth') for ch in channels):
        print("\n4. Testing common credentials...")
        print("-" * 70)

        # Take first channel that requires auth
        auth_channel = next(ch for ch in channels if ch.get('requires_auth'))
        test_url = auth_channel['url']

        cred_results = tester.test_common_credentials(test_url)

        if cred_results:
            print(f"\nFound {len(cred_results)} working credential(s):")
            for item in cred_results:
                print(f"\n  Username: {item['username']}")
                print(f"  Password: {item['password']}")
                print(f"  Response time: {item['result']['response_time']:.3f}s")
        else:
            print("\nNo working credentials found with common defaults")

    # Example 5: Export results
    print("\n5. Exporting results...")
    print("-" * 70)

    if channels:
        formatter.export_json(channels, 'channels.json')
        formatter.export_csv(channels, 'channels.csv')
        print("\nResults exported to:")
        print("  - channels.json")
        print("  - channels.csv")

    print("\n" + "=" * 70)
    print("Scan complete! Check scan.log for detailed logs.")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
