#!/usr/bin/env python3
"""
Basic functionality tests for RTSP Network Scanner
Run this before publishing to PyPI
"""

import sys
import tempfile
import os

def test_imports():
    """Test all module imports"""
    print("Test 1: Testing imports...")
    try:
        from rtsp_scanner.core.port_scanner import PortScanner
        from rtsp_scanner.core.rtsp_tester import RTSPTester
        from rtsp_scanner.core.channel_scanner import ChannelScanner
        from rtsp_scanner.core.camera_checker import CameraChecker
        from rtsp_scanner.utils.logger import setup_logger
        from rtsp_scanner.utils.output import OutputFormatter
        print("  ✓ All modules import successfully")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_url_validation():
    """Test URL validation"""
    print("\nTest 2: Testing URL validation...")
    try:
        from rtsp_scanner.core.rtsp_tester import RTSPTester
        tester = RTSPTester()

        # Valid URL
        is_valid, msg = tester.validate_rtsp_url('rtsp://192.168.1.100:554/stream')
        assert is_valid, f"Valid URL failed: {msg}"

        # Invalid URL
        is_valid, msg = tester.validate_rtsp_url('http://invalid')
        assert not is_valid, "Invalid URL should fail"

        print("  ✓ URL validation works")
        return True
    except Exception as e:
        print(f"  ✗ URL validation failed: {e}")
        return False


def test_url_parsing():
    """Test URL parsing"""
    print("\nTest 3: Testing URL parsing...")
    try:
        from rtsp_scanner.core.rtsp_tester import RTSPTester
        tester = RTSPTester()

        parsed = tester.parse_rtsp_url('rtsp://admin:pass@192.168.1.100:8554/stream')
        assert parsed['hostname'] == '192.168.1.100', "Hostname mismatch"
        assert parsed['port'] == 8554, "Port mismatch"
        assert parsed['username'] == 'admin', "Username mismatch"
        assert parsed['password'] == 'pass', "Password mismatch"
        assert parsed['path'] == '/stream', "Path mismatch"

        print("  ✓ URL parsing works")
        return True
    except Exception as e:
        print(f"  ✗ URL parsing failed: {e}")
        return False


def test_port_scanner():
    """Test PortScanner initialization"""
    print("\nTest 4: Testing PortScanner...")
    try:
        from rtsp_scanner.core.port_scanner import PortScanner, ProgressBar

        scanner = PortScanner(timeout=1.0, max_workers=10)
        assert scanner.timeout == 1.0, "Timeout mismatch"
        assert scanner.max_workers == 10, "Workers mismatch"

        # Test ProgressBar class
        progress = ProgressBar(100, prefix="Scanning")
        assert progress.total == 100, "ProgressBar total mismatch"

        print("  ✓ PortScanner initialization works")
        return True
    except Exception as e:
        print(f"  ✗ PortScanner failed: {e}")
        return False


def test_channel_scanner():
    """Test ChannelScanner initialization"""
    print("\nTest 5: Testing ChannelScanner...")
    try:
        from rtsp_scanner.core.channel_scanner import ChannelScanner, ProgressBar

        scanner = ChannelScanner(timeout=2.0, max_workers=5)
        assert scanner.timeout == 2.0, "Timeout mismatch"
        assert scanner.max_workers == 5, "Workers mismatch"
        assert len(scanner.COMMON_PATHS) > 0, "No common paths"

        # Test ProgressBar class
        progress = ProgressBar(10, prefix="Test")
        assert progress.total == 10, "ProgressBar total mismatch"
        assert progress.prefix == "Test", "ProgressBar prefix mismatch"

        print("  ✓ ChannelScanner initialization works")
        return True
    except Exception as e:
        print(f"  ✗ ChannelScanner failed: {e}")
        return False


def test_logger():
    """Test logger functionality"""
    print("\nTest 6: Testing Logger...")
    try:
        from rtsp_scanner.utils.logger import setup_logger

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_file = f.name

        logger = setup_logger(debug=True, log_file=log_file)
        logger.info('Test message')
        logger.debug('Debug message')

        assert os.path.exists(log_file), "Log file not created"

        with open(log_file) as f:
            content = f.read()
            assert 'Test message' in content, "Info message not logged"
            assert 'Debug message' in content, "Debug message not logged"

        os.unlink(log_file)
        print("  ✓ Logger works")
        return True
    except Exception as e:
        print(f"  ✗ Logger failed: {e}")
        return False


def test_output_formatter():
    """Test output formatter"""
    print("\nTest 7: Testing OutputFormatter...")
    try:
        from rtsp_scanner.utils.output import OutputFormatter

        formatter = OutputFormatter()
        results = [{'host': '192.168.1.1', 'port': 554, 'status': 'open'}]

        # JSON formatting
        json_out = formatter.format_json(results, pretty=True)
        assert '192.168.1.1' in json_out, "JSON formatting failed"

        # Table formatting
        table = formatter.format_table(results, ['host', 'port', 'status'])
        assert '192.168.1.1' in table, "Table formatting failed"
        assert '554' in table, "Port not in table"

        print("  ✓ OutputFormatter works")
        return True
    except Exception as e:
        print(f"  ✗ OutputFormatter failed: {e}")
        return False


def test_url_generation():
    """Test URL generation"""
    print("\nTest 8: Testing URL generation...")
    try:
        from rtsp_scanner.core.rtsp_tester import RTSPTester

        tester = RTSPTester()
        url = tester.generate_rtsp_url('192.168.1.100', 554, '/stream', 'admin', 'pass')
        expected = 'rtsp://admin:pass@192.168.1.100:554/stream'
        assert url == expected, f"URL mismatch: {url} != {expected}"

        print("  ✓ URL generation works")
        return True
    except Exception as e:
        print(f"  ✗ URL generation failed: {e}")
        return False


def test_exports():
    """Test export functionality"""
    print("\nTest 9: Testing export functionality...")
    try:
        from rtsp_scanner.utils.output import OutputFormatter
        import json
        import csv

        formatter = OutputFormatter()
        results = [{'host': '192.168.1.1', 'port': 554, 'status': 'open'}]

        # JSON export
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json_file = f.name

        formatter.export_json(results, json_file)
        assert os.path.exists(json_file), "JSON file not created"

        with open(json_file) as f:
            data = json.load(f)
            assert len(data) == 1, "JSON data mismatch"

        os.unlink(json_file)

        # CSV export
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            csv_file = f.name

        formatter.export_csv(results, csv_file)
        assert os.path.exists(csv_file), "CSV file not created"

        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1, "CSV data mismatch"

        os.unlink(csv_file)

        print("  ✓ Export functionality works")
        return True
    except Exception as e:
        print(f"  ✗ Export failed: {e}")
        return False


def test_package_version():
    """Test package metadata"""
    print("\nTest 10: Testing package metadata...")
    try:
        import rtsp_scanner

        assert hasattr(rtsp_scanner, '__version__'), "No version attribute"
        assert rtsp_scanner.__version__ == '2.5.1', f"Version mismatch: expected 2.5.1, got {rtsp_scanner.__version__}"

        print("  ✓ Package metadata correct")
        return True
    except Exception as e:
        print(f"  ✗ Package metadata failed: {e}")
        return False


def test_camera_checker():
    """Test CameraChecker initialization"""
    print("\nTest 11: Testing CameraChecker...")
    try:
        from rtsp_scanner.core.camera_checker import CameraChecker

        checker = CameraChecker(timeout=5.0)
        assert checker.timeout == 5.0, "Timeout mismatch"

        # Test ffmpeg availability check (should not crash)
        available = checker.is_ffmpeg_available()
        assert isinstance(available, bool), "is_ffmpeg_available should return bool"

        print("  ✓ CameraChecker initialization works")
        return True
    except Exception as e:
        print(f"  ✗ CameraChecker failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("RTSP Network Scanner - Package Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_url_validation,
        test_url_parsing,
        test_port_scanner,
        test_channel_scanner,
        test_logger,
        test_output_formatter,
        test_url_generation,
        test_exports,
        test_package_version,
        test_camera_checker,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Summary: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n✓ All tests passed! Package is ready to publish.")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed. Please fix before publishing.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
