# RTSP Network Scanner

Network RTSP stream scanner and debugger.

## Install

```bash
pip install rtsp-network-scanner
```

## Usage

```bash
# Auto-scan your local network
rtsp-network-scanner network

# Scan specific network
rtsp-network-scanner network 192.168.1.0/24

# Scan single host
rtsp-network-scanner ports 192.168.1.100

# Test RTSP URL
rtsp-network-scanner test rtsp://192.168.1.100:554/stream

# Quick channel scan
rtsp-network-scanner quick 192.168.1.100
```

## Commands

- `network` - Scan network (auto-detects if no network specified)
- `ports` - Scan single host
- `range` - Scan IP range
- `test` - Test RTSP URL
- `validate` - Validate URL
- `channels` - Scan for channels
- `quick` - Quick scan
- `numbered` - Scan numbered channels
- `credentials` - Test credentials

## Options

- `--debug` - Debug logging
- `--log-file FILE` - Log to file
- `--output FILE` - Export (JSON/CSV)
- `--timeout SECONDS` - Timeout (default: 2.0s)
- `--workers NUM` - Workers (default: 50)

## Links

- [GitHub](https://github.com/sssanjaya/rtsp-network-scanner)
- [PyPI](https://pypi.org/project/rtsp-network-scanner/)

## License

MIT

## Author

Sanjay H
