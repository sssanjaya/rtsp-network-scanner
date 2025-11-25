# RTSP Scanner - Project Summary

## Overview

A comprehensive Python application for scanning, debugging, and testing RTSP (Real-Time Streaming Protocol) streams in networks. This tool helps discover RTSP cameras, test connectivity, identify available channels, and validate RTSP URLs.

## Project Information

- **Version**: 1.0.0
- **Language**: Python 3.7+
- **Dependencies**: None (uses only Python standard library)
- **License**: MIT

## Package Structure

```
rtsp-scanner/
├── rtsp_scanner/              # Main package
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Command-line interface
│   ├── core/                 # Core functionality modules
│   │   ├── __init__.py
│   │   ├── port_scanner.py   # Network port scanning
│   │   ├── rtsp_tester.py    # RTSP URL testing & validation
│   │   └── channel_scanner.py # Channel discovery
│   └── utils/                # Utility modules
│       ├── __init__.py
│       ├── logger.py         # Logging utilities
│       └── output.py         # Output formatting
├── examples/                  # Example scripts
│   ├── basic_scan.py         # Basic usage examples
│   └── network_scan.py       # Network-wide scan example
├── dist/                      # Built packages
│   ├── rtsp-scanner-1.0.0.tar.gz           # Source distribution
│   └── rtsp_scanner-1.0.0-py3-none-any.whl # Wheel package
├── setup.py                   # Setup configuration
├── pyproject.toml            # Modern Python project config
├── requirements.txt          # Dependencies (none required)
├── MANIFEST.in               # Package manifest
├── LICENSE                   # MIT License
├── README.md                 # Full documentation
├── QUICKSTART.md             # Quick start guide
└── PROJECT_SUMMARY.md        # This file
```

## Core Features

### 1. Port Scanner (`port_scanner.py`)
- Scan entire networks (CIDR notation) for open RTSP ports
- Scan IP ranges for RTSP services
- Scan individual hosts
- Multi-threaded for performance (configurable workers)
- Default RTSP ports: 554, 8554, 7447, 5554, 88, 8000, 8080, 8888

### 2. RTSP Tester (`rtsp_tester.py`)
- Validate RTSP URL format
- Parse RTSP URLs into components
- Test RTSP connections with DESCRIBE requests
- Support for authentication
- Test common default credentials
- Generate RTSP URLs from components

### 3. Channel Scanner (`channel_scanner.py`)
- Discover available RTSP channels on cameras
- Support for multiple camera manufacturers:
  - Hikvision
  - Dahua
  - Axis
  - Foscam
  - Amcrest
  - TP-Link
  - Generic ONVIF cameras
- Test with credential combinations
- Quick scan mode for common paths only
- Numbered channel scanning (e.g., channel1, channel2)

### 4. Logger (`logger.py`)
- Configurable logging levels
- Debug mode with detailed output
- File logging support
- Formatted output for CLI and debugging

### 5. Output Formatter (`output.py`)
- ASCII table formatting
- JSON export
- CSV export
- Summary reports
- Customizable field display

## CLI Commands

The application provides 9 main commands:

1. **scan-network** - Scan network range for RTSP ports
2. **scan-ports** - Scan ports on single host
3. **scan-range** - Scan IP address range
4. **test-url** - Test specific RTSP URL
5. **validate-url** - Validate URL format
6. **scan-channels** - Discover channels on camera
7. **quick-scan** - Quick channel scan (common paths)
8. **scan-numbered** - Scan numbered channels (1-16)
9. **test-credentials** - Test common credentials

## Usage Examples

### Command Line

```bash
# Validate URL
python3 -m rtsp_scanner.cli validate-url rtsp://192.168.1.100:554/stream

# Scan network
python3 -m rtsp_scanner.cli scan-network 192.168.1.0/24 --output results.json

# Quick channel scan
python3 -m rtsp_scanner.cli quick-scan 192.168.1.100 --debug

# Test with credentials
python3 -m rtsp_scanner.cli test-url rtsp://192.168.1.100:554/stream \
    --username admin --password admin
```

### Python API

```python
from rtsp_scanner.core.port_scanner import PortScanner
from rtsp_scanner.core.rtsp_tester import RTSPTester
from rtsp_scanner.core.channel_scanner import ChannelScanner

# Port scanning
scanner = PortScanner(timeout=2.0, max_workers=50)
results = scanner.scan_network('192.168.1.0/24')

# URL testing
tester = RTSPTester(timeout=5.0)
result = tester.test_rtsp_connection('rtsp://192.168.1.100:554/stream')

# Channel scanning
channel_scanner = ChannelScanner(timeout=5.0, max_workers=20)
channels = channel_scanner.quick_scan('192.168.1.100')
```

## Installation Methods

### Method 1: Install from wheel
```bash
pip install dist/rtsp_scanner-1.0.0-py3-none-any.whl
```

### Method 2: Install from source
```bash
pip install .
```

### Method 3: Run directly
```bash
python3 -m rtsp_scanner.cli [command]
```

## Built Packages

Two distribution packages are available in the `dist/` directory:

1. **Source Distribution**: `rtsp-scanner-1.0.0.tar.gz`
   - Complete source code
   - Platform independent
   - Can be built on any system

2. **Wheel Package**: `rtsp_scanner-1.0.0-py3-none-any.whl`
   - Pre-built binary distribution
   - Fast installation
   - Python 3.7+ compatible
   - Platform independent

## Technical Details

### Architecture
- **Multi-threaded**: Uses `concurrent.futures.ThreadPoolExecutor` for parallel scanning
- **Socket-based**: Low-level socket operations for port scanning
- **RTSP Protocol**: Implements RTSP DESCRIBE method for URL testing
- **Zero Dependencies**: Uses only Python standard library

### Performance
- Configurable timeout (default: 2.0 seconds)
- Configurable workers (default: 50 concurrent threads)
- Optimized for network scanning
- Progress reporting for long-running scans

### Security Features
- No destructive operations
- Read-only network operations
- Designed for authorized testing only
- Clear security warnings in documentation

## Configuration Options

### Global Options
- `--debug`: Enable debug logging
- `--log-file FILE`: Save logs to file
- `--output FILE`: Export results (JSON/CSV)
- `--timeout SECONDS`: Connection timeout
- `--workers NUM`: Max concurrent workers

### Common Defaults
- Timeout: 2.0 seconds
- Workers: 50 (port scan) / 20 (channel scan)
- RTSP Port: 554

## Supported Camera Paths

Includes 50+ path patterns for major camera manufacturers:

**Hikvision**: `/Streaming/Channels/101`, `/h264/ch1/main/av_stream`
**Dahua**: `/cam/realmonitor?channel=1&subtype=0`
**Axis**: `/axis-media/media.amp`
**Foscam**: `/videoMain`, `/video.h264`
**Generic**: `/stream`, `/live`, `/video`, `/h264`

## Common Credentials Tested

The tool tests these common default credentials:
- admin/admin
- admin/(blank)
- admin/12345
- admin/password
- root/root
- root/(blank)
- (blank)/(blank)

## Testing

The package has been tested with:
- Python 3.9.6 on macOS
- URL validation functionality
- CLI command execution
- Package building (source & wheel)

## Future Enhancements

Potential features for future versions:
- Unit tests with pytest
- ONVIF protocol support
- Stream playback/preview
- Bandwidth measurement
- Authentication method detection
- Web interface
- Report generation
- Database storage

## Documentation

- **README.md**: Complete documentation and API reference
- **QUICKSTART.md**: Quick start guide with common examples
- **PROJECT_SUMMARY.md**: This file - project overview
- **Examples**: Working Python scripts in `examples/` directory

## Use Cases

1. **Network Administration**: Discover RTSP cameras on network
2. **Security Testing**: Identify cameras with default credentials
3. **Troubleshooting**: Debug RTSP connectivity issues
4. **Integration**: Integrate with monitoring systems
5. **Inventory**: Document RTSP resources on network

## Legal & Security Notice

This tool is designed for:
- Authorized security assessments
- Testing your own infrastructure
- Network administration
- Educational purposes

**Warning**: Only use on networks/devices you own or have explicit permission to test.

## Version History

### Version 1.0.0 (2025-11-25)
- Initial release
- Network port scanning
- RTSP URL testing and validation
- Channel discovery
- Credential testing
- Export to JSON/CSV
- Comprehensive CLI interface
- Python API
- Full documentation

## Author & License

**License**: MIT License (see LICENSE file)
**Author**: RTSP Scanner Team

## Support

For issues or questions:
- Check README.md for documentation
- See QUICKSTART.md for examples
- Review example scripts in `examples/`

## Build Information

**Built on**: 2025-11-25
**Build system**: setuptools
**Package format**: wheel + source distribution
**Python requirement**: >=3.7
**Platform**: Any (pure Python)

## Getting Started

1. Read QUICKSTART.md for basic usage
2. Try the example scripts in `examples/`
3. Run CLI help: `python3 -m rtsp_scanner.cli --help`
4. See README.md for complete documentation

---

**Project Location**: `/Users/sanjayhona/workspace/SRE`
**Package Name**: `rtsp-scanner`
**Module Name**: `rtsp_scanner`
