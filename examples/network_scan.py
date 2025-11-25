#!/usr/bin/env python3
"""
Network-wide RTSP Scanner Example

This example demonstrates scanning an entire network for RTSP cameras
and discovering their channels.
"""

from rtsp_scanner.core.port_scanner import PortScanner
from rtsp_scanner.core.channel_scanner import ChannelScanner
from rtsp_scanner.utils.logger import setup_logger
from rtsp_scanner.utils.output import OutputFormatter


def main():
    """Main network scanning example"""

    # Configuration
    NETWORK = '192.168.1.0/24'  # Change this to your network
    TIMEOUT = 2.0
    MAX_WORKERS = 100

    # Setup logger
    logger = setup_logger(debug=False, log_file='network_scan.log')
    formatter = OutputFormatter()

    print("=" * 70)
    print(f"Scanning Network: {NETWORK}")
    print("=" * 70)

    # Step 1: Scan network for open RTSP ports
    print("\nStep 1: Scanning for open RTSP ports...")
    print("-" * 70)

    scanner = PortScanner(timeout=TIMEOUT, max_workers=MAX_WORKERS, logger=logger)
    # Progress bar is shown by default, set show_progress=False to disable
    port_results = scanner.scan_network(NETWORK, show_progress=True)

    if not port_results:
        print("\nNo open RTSP ports found on the network.")
        return

    print(f"\nFound {len(port_results)} open RTSP port(s):")
    print(formatter.format_table(port_results, ['host', 'port', 'status', 'response_time']))

    # Export port scan results
    formatter.export_json(port_results, 'port_scan_results.json')
    print("\nPort scan results saved to: port_scan_results.json")

    # Step 2: Scan each found host for available channels
    print("\n\nStep 2: Discovering channels on found hosts...")
    print("-" * 70)

    channel_scanner = ChannelScanner(timeout=5.0, max_workers=20, logger=logger)
    all_channels = []

    # Get unique hosts
    hosts = list(set(result['host'] for result in port_results))

    for i, host in enumerate(hosts, 1):
        # Get port(s) for this host
        host_ports = [r['port'] for r in port_results if r['host'] == host]

        for port in host_ports:
            # Progress bar shows scanning status
            channels = channel_scanner.quick_scan(host, port, show_progress=True)

            if channels:
                print(f"  Found {len(channels)} channel(s) on {host}:{port}")
                for channel in channels:
                    channel['host'] = host  # Add host info
                    all_channels.append(channel)
            else:
                print(f"  No channels found on {host}:{port}")

    # Step 3: Display and export channel results
    print("\n\nStep 3: Channel Discovery Summary")
    print("-" * 70)

    if all_channels:
        print(f"\nTotal channels discovered: {len(all_channels)}")

        # Separate by authentication requirement
        accessible = [ch for ch in all_channels if ch.get('status_code') == 200]
        requires_auth = [ch for ch in all_channels if ch.get('status_code') == 401]

        print(f"  - Accessible without auth: {len(accessible)}")
        print(f"  - Requires authentication: {len(requires_auth)}")

        print("\nAll discovered channels:")
        print(formatter.format_table(
            all_channels,
            ['host', 'path', 'status_code', 'response_time', 'requires_auth']
        ))

        # Export channel results
        formatter.export_json(all_channels, 'channel_scan_results.json')
        formatter.export_csv(all_channels, 'channel_scan_results.csv')

        print("\nChannel scan results saved to:")
        print("  - channel_scan_results.json")
        print("  - channel_scan_results.csv")

        # Generate working URLs
        print("\n\nWorking RTSP URLs:")
        print("-" * 70)
        for channel in accessible:
            url = f"rtsp://{channel['host']}:{channel.get('port', 554)}{channel['path']}"
            print(f"  {url}")

    else:
        print("\nNo channels discovered on any host.")

    print("\n" + "=" * 70)
    print("Network scan complete! Check network_scan.log for details.")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
