# RTSP Scanner - Quick Start Guide

## Installation

### Option 1: Install from built wheel package

```bash
pip install dist/rtsp_scanner-1.0.0-py3-none-any.whl
```

### Option 2: Install from source

```bash
pip install .
```

### Option 3: Run directly without installation

```bash
python3 -m rtsp_scanner.cli [command]
```

## Basic Usage

### 1. Validate an RTSP URL

```bash
python3 -m rtsp_scanner.cli validate-url rtsp://192.168.1.100:554/stream
```

### 2. Scan a single host for open RTSP ports

```bash
python3 -m rtsp_scanner.cli scan-ports 192.168.1.100
```

### 3. Scan an entire network

```bash
python3 -m rtsp_scanner.cli scan-network 192.168.1.0/24 --output results.json
```

### 4. Test a specific RTSP URL

```bash
python3 -m rtsp_scanner.cli test-url rtsp://192.168.1.100:554/stream
```

With authentication:

```bash
python3 -m rtsp_scanner.cli test-url rtsp://192.168.1.100:554/stream \
    --username admin --password admin
```

### 5. Quick channel scan

Scan for available channels on a camera:

```bash
python3 -m rtsp_scanner.cli quick-scan 192.168.1.100
```

### 6. Full channel scan with common credentials

```bash
python3 -m rtsp_scanner.cli scan-channels 192.168.1.100 --with-creds
```

### 7. Test common default credentials

```bash
python3 -m rtsp_scanner.cli test-credentials rtsp://192.168.1.100:554/
```

## Debug Mode

Enable debug logging for detailed output:

```bash
python3 -m rtsp_scanner.cli scan-network 192.168.1.0/24 --debug --log-file scan.log
```

## Export Results

Export scan results to JSON or CSV:

```bash
# JSON format
python3 -m rtsp_scanner.cli scan-channels 192.168.1.100 --output results.json

# CSV format
python3 -m rtsp_scanner.cli scan-network 192.168.1.0/24 --output results.csv
```

## Python API Examples

### Scan network for RTSP ports

```python
from rtsp_scanner.core.port_scanner import PortScanner
from rtsp_scanner.utils.logger import setup_logger

logger = setup_logger(debug=True)
scanner = PortScanner(timeout=2.0, max_workers=50, logger=logger)

results = scanner.scan_network('192.168.1.0/24')
print(f"Found {len(results)} open RTSP ports")

for result in results:
    print(f"  {result['host']}:{result['port']} - {result['status']}")
```

### Test RTSP URL

```python
from rtsp_scanner.core.rtsp_tester import RTSPTester

tester = RTSPTester(timeout=5.0)

# Validate URL
is_valid, message = tester.validate_rtsp_url('rtsp://192.168.1.100:554/stream')
print(f"Valid: {is_valid} - {message}")

# Test connection
result = tester.test_rtsp_connection('rtsp://192.168.1.100:554/stream')
print(f"Reachable: {result['reachable']}")
print(f"Status Code: {result.get('status_code')}")
```

### Scan for channels

```python
from rtsp_scanner.core.channel_scanner import ChannelScanner

scanner = ChannelScanner(timeout=5.0, max_workers=20)

# Quick scan
channels = scanner.quick_scan('192.168.1.100')

print(f"Found {len(channels)} channels:")
for channel in channels:
    print(f"  {channel['path']} - Status: {channel['status_code']}")
```

## Performance Tuning

### Increase timeout for slow networks

```bash
python3 -m rtsp_scanner.cli scan-network 192.168.1.0/24 --timeout 5
```

### Increase workers for faster scanning

```bash
python3 -m rtsp_scanner.cli scan-network 192.168.1.0/24 --workers 100
```

## Common RTSP Ports

The scanner checks these ports by default:
- 554 (Standard RTSP)
- 8554
- 7447
- 5554
- 88
- 8000
- 8080
- 8888

To scan custom ports:

```bash
python3 -m rtsp_scanner.cli scan-ports 192.168.1.100 --ports 554 8554 10554
```

## Security Notice

This tool is designed for authorized security testing and network administration only.
Always ensure you have proper authorization before scanning networks or devices.

## Troubleshooting

### Module not found error

If you get "No module named rtsp_scanner", make sure you're running from the project root:

```bash
cd /Users/sanjayhona/workspace/SRE
python3 -m rtsp_scanner.cli --help
```

### Permission denied

If you get permission errors during installation, use:

```bash
pip install --user dist/rtsp_scanner-1.0.0-py3-none-any.whl
```

### Connection timeouts

If you experience many timeouts, increase the timeout value:

```bash
python3 -m rtsp_scanner.cli scan-network 192.168.1.0/24 --timeout 5
```

## Example Workflow

Complete workflow to discover RTSP cameras on your network:

```bash
# 1. Scan network for open RTSP ports
python3 -m rtsp_scanner.cli scan-network 192.168.1.0/24 --output ports.json

# 2. For each found host, scan for channels
python3 -m rtsp_scanner.cli quick-scan 192.168.1.100 --output channels.json

# 3. Test credentials if needed
python3 -m rtsp_scanner.cli test-credentials rtsp://192.168.1.100:554/

# 4. View detailed logs
python3 -m rtsp_scanner.cli scan-channels 192.168.1.100 --debug --log-file debug.log
```

## Further Reading

See README.md for complete documentation and API reference.
