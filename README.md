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

# Scan with credentials (validates auth, shows codec/resolution)
rtsp-network-scanner scan -u admin -p password

# Check if cameras are actually working (requires ffmpeg)
rtsp-network-scanner scan --check

# Simple output (minimal info)
rtsp-network-scanner scan --simple

# Detailed output (all info)
rtsp-network-scanner scan --detailed

# Skip channel discovery (ports only)
rtsp-network-scanner scan --skip-channels
```

## What it does

One command scans everything:
1. Finds hosts with open RTSP ports (554, 8554, 7447, etc.)
2. Discovers available channels on each camera (supports Hikvision, Dahua, Axis, etc.)
3. Shows channel status: ✓ OK, ✗ Auth Error, etc.
4. Validates credentials and shows codec/resolution

**Example output:**
```
Found 1 camera(s) with 8 channel(s)

+--------------+------+-------------------------+-------------+--------+
| host         | port | path                    | stream_type | status |
+--------------+------+-------------------------+-------------+--------+
| 192.168.1.10 | 554  | /Streaming/Channels/101 | Main        | ✓ OK   |
| 192.168.1.10 | 554  | /Streaming/Channels/102 | Sub         | ✓ OK   |
| 192.168.1.10 | 554  | /Streaming/Channels/201 | Main        | ✗ Auth |
+--------------+------+-------------------------+-------------+--------+
```

**Status indicators:**
- `✓ OK` - Channel accessible with provided credentials
- `✗ Auth` - Channel exists but credentials are wrong/missing
- `⊘ Forbidden` - Access denied

## Options

| Option | Description |
|--------|-------------|
| `-u, --username` | Username for authentication |
| `-p, --password` | Password for authentication |
| `--check` | Verify cameras work using ffmpeg |
| `--simple` | Minimal output (host, port, status) |
| `--detailed` | Full output (codec, resolution, fps, bitrate) |
| `--skip-channels` | Skip channel discovery (ports only) |
| `--timeout SECONDS` | Connection timeout (default: 2.0s) |
| `--workers NUM` | Concurrent workers (default: 50) |
| `--output FILE` | Export results (JSON/CSV) |
| `--debug` | Enable debug logging |
| `--log-file FILE` | Log to file |

## Supported Cameras

- **Hikvision** - All 8 channels (101-802)
- **Dahua / Amcrest** - Multiple channels
- **Axis** - VAPIX streams
- **Foscam** - Main/Sub streams
- **Generic** - Common RTSP paths

## Links

- [GitHub](https://github.com/sssanjaya/rtsp-network-scanner)
- [PyPI](https://pypi.org/project/rtsp-network-scanner/)

## License

MIT

## Author

Sanjay H
