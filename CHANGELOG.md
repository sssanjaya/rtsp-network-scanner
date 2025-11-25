# Changelog

All notable changes to the RTSP Scanner project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Unit tests with pytest
- ONVIF protocol support
- Stream playback/preview functionality
- Bandwidth measurement
- Authentication method detection
- Web interface
- Report generation in HTML/PDF
- Database storage support

## [2.3.1] - 2025-11-25

### Fixed
- Updated documentation and examples for progress bar feature
- Fixed test assertions for version checking

## [2.3.0] - 2025-11-25

### Added
- Progress bars for port scanning and channel discovery
  - Shows real-time progress with completion percentage
  - Displays count of found items during scan
  - Thread-safe implementation for concurrent operations
- `show_progress` parameter to scanner methods for controlling progress display

### Changed
- Reduced verbose logging during scans
  - "Testing RTSP connection" messages moved to debug level
  - Socket errors, timeouts, and path not found messages moved to debug level
  - Cleaner output without timestamp clutter during normal operation
- CLI output improved with cleaner formatting using print() instead of logger
- Progress bars disabled automatically when `--debug` flag is used

### Technical Details
- Added `ProgressBar` class to both `port_scanner.py` and `channel_scanner.py`
- Uses carriage return (`\r`) for in-place terminal updates
- No new external dependencies (uses Python standard library only)

## [1.0.0] - 2025-11-25

### Added
- Initial release of RTSP Scanner
- Network port scanning functionality
  - Scan entire networks in CIDR notation
  - Scan IP ranges
  - Scan individual hosts
  - Multi-threaded scanning with configurable workers
- RTSP URL testing and validation
  - URL format validation
  - URL parsing into components
  - Connection testing with RTSP DESCRIBE
  - Authentication support
  - Common credential testing
- Channel discovery for RTSP cameras
  - 50+ path patterns for major camera manufacturers
  - Support for Hikvision, Dahua, Axis, Foscam, Amcrest, TP-Link
  - Quick scan mode for fast discovery
  - Numbered channel scanning
  - Credential brute-forcing capability
- Comprehensive CLI with 9 commands
  - scan-network: Scan network ranges
  - scan-ports: Scan single hosts
  - scan-range: Scan IP ranges
  - test-url: Test specific RTSP URLs
  - validate-url: Validate URL format
  - scan-channels: Discover camera channels
  - quick-scan: Fast channel discovery
  - scan-numbered: Scan numbered channels
  - test-credentials: Test default credentials
- Python API for programmatic usage
- Advanced logging with debug mode
- Output formatting
  - ASCII table display
  - JSON export
  - CSV export
  - Summary reports
- Documentation
  - Comprehensive README
  - Quick start guide
  - Example scripts
  - API documentation
- Package distribution
  - Source distribution (tar.gz)
  - Wheel package
  - No external dependencies

### Technical Details
- Built with Python 3.7+ compatibility
- Uses only Python standard library (no external dependencies)
- Multi-threaded architecture for performance
- Socket-based network operations
- RTSP protocol implementation
- 1,367 lines of code
- MIT License

### Security
- Designed for authorized testing only
- Read-only operations
- No destructive capabilities
- Clear security warnings in documentation

## Version History

### Version Numbering Scheme

This project follows [Semantic Versioning](https://semver.org/):

- MAJOR version: Incompatible API changes
- MINOR version: Add functionality (backwards compatible)
- PATCH version: Bug fixes (backwards compatible)

### Examples

- `1.0.0` - Initial release
- `1.0.1` - Bug fix release
- `1.1.0` - New feature added (backwards compatible)
- `2.0.0` - Breaking changes to API

## Contributing

When contributing, please:
1. Update this CHANGELOG with your changes
2. Follow semantic versioning
3. Add entries under [Unreleased] section
4. Move to versioned section when releasing

### Change Categories

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

[Unreleased]: https://github.com/yourusername/rtsp-scanner/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/rtsp-scanner/releases/tag/v1.0.0
