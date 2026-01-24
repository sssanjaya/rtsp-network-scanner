# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/claude-code) when working with this repository.

## Project Overview

RTSP Network Scanner is a Python CLI tool that scans networks for RTSP cameras. It discovers hosts with open RTSP ports, identifies camera manufacturers, and enumerates available video channels.

## Common Commands

```bash
# Install in development mode
pip install -e .

# Run the scanner
rtsp-network-scanner scan                    # Auto-detect local network
rtsp-network-scanner scan 192.168.1.0/24     # Scan specific network
rtsp-network-scanner scan 192.168.1.100      # Scan single host
rtsp-network-scanner scan -u admin -p pass   # With credentials

# Run tests
python test_basic.py

# Build package
python -m build

# Publish to PyPI
python -m twine upload dist/*
```

## Project Structure

```
rtsp_scanner/
├── cli.py              # Main CLI entry point (argparse)
├── core/
│   ├── port_scanner.py    # Network port scanning
│   ├── rtsp_tester.py     # RTSP protocol testing
│   ├── channel_scanner.py # Camera channel discovery
│   └── camera_checker.py  # ffmpeg-based health checks
└── utils/
    ├── logger.py          # Logging setup
    ├── network.py         # Network utilities (IP detection)
    └── output.py          # Output formatting (table, JSON, CSV)
```

## Key Architecture

1. **Port Scanner** (`port_scanner.py`): Scans for open RTSP ports (554, 8554, 7447, etc.) using concurrent connections
2. **RTSP Tester** (`rtsp_tester.py`): Validates RTSP protocol and detects manufacturer from server headers
3. **Channel Scanner** (`channel_scanner.py`): Discovers available channels using manufacturer-specific URL patterns (Hikvision, Dahua, Axis, etc.)
4. **Camera Checker** (`camera_checker.py`): Uses ffprobe/ffmpeg to verify streams are actually working

## Supported Camera Manufacturers

- Hikvision (channels 101-802)
- Dahua/Amcrest
- Axis (VAPIX)
- Foscam
- Generic RTSP paths

## Code Conventions

- Use `concurrent.futures.ThreadPoolExecutor` for parallel operations
- Always handle exceptions from `future.result()` in thread pools
- Channel status values: `ok`, `auth_error`, `forbidden`, `not_found`, `error`
- URL construction should handle None paths gracefully
