# RTSP Network Scanner

Scan networks for RTSP cameras - finds hosts, ports, and channels in one command.

## Install

```bash
pip install rtsp-network-scanner
```

## Usage

```bash
# Scan local network (auto-detected) - finds cameras, ports, and channels
rtsp-network-scanner scan

# Scan specific network
rtsp-network-scanner scan 192.168.1.0/24

# Scan single host
rtsp-network-scanner scan 192.168.1.100

# Scan with credentials (shows validation status, codec, resolution)
rtsp-network-scanner scan -u admin -p password

# Skip channel discovery (ports only)
rtsp-network-scanner scan --skip-channels
```

## What it does

One command scans everything:
1. Finds hosts with open RTSP ports (554, 8554, 7447, etc.)
2. Discovers available channels on each camera
3. Shows working RTSP URLs with response times

**Progress bars** show real-time scanning progress:
```
Port scan 192.168.1.0/24 [████████████████████░░░░░░░░░░░░░░░░░░░░] 1024/2032 (2 found)
Scanning 192.168.1.100:554 [████████████████████████████████████████] 61/61 (8 found)
```

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
