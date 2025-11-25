# RTSP Network Scanner

Scan networks for RTSP cameras, test streams, discover channels.

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

# Validate RTSP URL
rtsp-network-scanner validate rtsp://192.168.1.100:554/stream

# Scan for channels
rtsp-network-scanner channels 192.168.1.100
```

## Commands

- `network` - Scan network (auto-detects if no network specified)
- `ports` - Scan single host
- `validate` - Validate RTSP URL
- `channels` - Scan for channels

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
