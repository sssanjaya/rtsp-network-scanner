#!/bin/bash
# Comprehensive package testing script for RTSP Scanner

set -e

echo "=========================================="
echo "RTSP Network Scanner - Package Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++))
}

test_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Test 1: Import modules
echo "Test 1: Testing Python imports..."
python3 -c "
import sys
try:
    from rtsp_scanner.core.port_scanner import PortScanner
    from rtsp_scanner.core.rtsp_tester import RTSPTester
    from rtsp_scanner.core.channel_scanner import ChannelScanner
    from rtsp_scanner.utils.logger import setup_logger
    from rtsp_scanner.utils.output import OutputFormatter
    print('SUCCESS')
except Exception as e:
    print(f'FAILED: {e}')
    sys.exit(1)
" && test_pass "All modules import successfully" || test_fail "Module import failed"

echo ""

# Test 2: CLI help
echo "Test 2: Testing CLI help command..."
python3 -m rtsp_scanner.cli --help > /dev/null 2>&1 && \
    test_pass "CLI help works" || test_fail "CLI help failed"

echo ""

# Test 3: Validate URL functionality
echo "Test 3: Testing URL validation..."
python3 -c "
from rtsp_scanner.core.rtsp_tester import RTSPTester
tester = RTSPTester()
is_valid, msg = tester.validate_rtsp_url('rtsp://192.168.1.100:554/stream')
assert is_valid, f'Valid URL failed: {msg}'
is_valid, msg = tester.validate_rtsp_url('http://invalid')
assert not is_valid, 'Invalid URL passed'
print('URL validation works correctly')
" && test_pass "URL validation works" || test_fail "URL validation failed"

echo ""

# Test 4: Port scanner creation
echo "Test 4: Testing PortScanner initialization..."
python3 -c "
from rtsp_scanner.core.port_scanner import PortScanner
scanner = PortScanner(timeout=1.0, max_workers=10)
assert scanner.timeout == 1.0
assert scanner.max_workers == 10
print('PortScanner initialized correctly')
" && test_pass "PortScanner initialization works" || test_fail "PortScanner initialization failed"

echo ""

# Test 5: RTSP Tester URL parsing
echo "Test 5: Testing RTSP URL parsing..."
python3 -c "
from rtsp_scanner.core.rtsp_tester import RTSPTester
tester = RTSPTester()
parsed = tester.parse_rtsp_url('rtsp://admin:pass@192.168.1.100:8554/stream')
assert parsed['hostname'] == '192.168.1.100'
assert parsed['port'] == 8554
assert parsed['username'] == 'admin'
assert parsed['password'] == 'pass'
assert parsed['path'] == '/stream'
print('URL parsing works correctly')
" && test_pass "URL parsing works" || test_fail "URL parsing failed"

echo ""

# Test 6: Channel Scanner initialization
echo "Test 6: Testing ChannelScanner..."
python3 -c "
from rtsp_scanner.core.channel_scanner import ChannelScanner
scanner = ChannelScanner(timeout=2.0, max_workers=5)
assert scanner.timeout == 2.0
assert scanner.max_workers == 5
assert len(scanner.COMMON_PATHS) > 0
print('ChannelScanner initialized correctly')
" && test_pass "ChannelScanner initialization works" || test_fail "ChannelScanner initialization failed"

echo ""

# Test 7: Logger functionality
echo "Test 7: Testing Logger..."
python3 -c "
from rtsp_scanner.utils.logger import setup_logger
import tempfile
import os

with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
    log_file = f.name

logger = setup_logger(debug=True, log_file=log_file)
logger.info('Test message')
logger.debug('Debug message')

assert os.path.exists(log_file)
with open(log_file) as f:
    content = f.read()
    assert 'Test message' in content
    assert 'Debug message' in content

os.unlink(log_file)
print('Logger works correctly')
" && test_pass "Logger works" || test_fail "Logger failed"

echo ""

# Test 8: Output formatter
echo "Test 8: Testing OutputFormatter..."
python3 -c "
from rtsp_scanner.utils.output import OutputFormatter
formatter = OutputFormatter()

# Test JSON formatting
results = [{'host': '192.168.1.1', 'port': 554, 'status': 'open'}]
json_out = formatter.format_json(results, pretty=True)
assert '192.168.1.1' in json_out

# Test table formatting
table = formatter.format_table(results, ['host', 'port', 'status'])
assert '192.168.1.1' in table
assert '554' in table

print('OutputFormatter works correctly')
" && test_pass "OutputFormatter works" || test_fail "OutputFormatter failed"

echo ""

# Test 9: CLI validate-url command
echo "Test 9: Testing CLI validate-url command..."
python3 -m rtsp_scanner.cli validate-url rtsp://test.com:554/stream 2>&1 | \
    grep -q "Valid: True" && \
    test_pass "CLI validate-url works" || test_fail "CLI validate-url failed"

echo ""

# Test 10: Package metadata
echo "Test 10: Checking package metadata..."
python3 -c "
import rtsp_scanner
assert hasattr(rtsp_scanner, '__version__')
assert rtsp_scanner.__version__ == '1.0.0'
print('Package metadata correct')
" && test_pass "Package metadata correct" || test_fail "Package metadata failed"

echo ""

# Test 11: Generate RTSP URL
echo "Test 11: Testing RTSP URL generation..."
python3 -c "
from rtsp_scanner.core.rtsp_tester import RTSPTester
tester = RTSPTester()
url = tester.generate_rtsp_url('192.168.1.100', 554, '/stream', 'admin', 'pass')
assert url == 'rtsp://admin:pass@192.168.1.100:554/stream'
print('URL generation works correctly')
" && test_pass "URL generation works" || test_fail "URL generation failed"

echo ""

# Test 12: Export functionality
echo "Test 12: Testing export functionality..."
python3 -c "
from rtsp_scanner.utils.output import OutputFormatter
import tempfile
import os
import json
import csv

formatter = OutputFormatter()
results = [{'host': '192.168.1.1', 'port': 554, 'status': 'open'}]

# Test JSON export
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
    json_file = f.name
formatter.export_json(results, json_file)
assert os.path.exists(json_file)
with open(json_file) as f:
    data = json.load(f)
    assert len(data) == 1
os.unlink(json_file)

# Test CSV export
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
    csv_file = f.name
formatter.export_csv(results, csv_file)
assert os.path.exists(csv_file)
with open(csv_file) as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    assert len(rows) == 1
os.unlink(csv_file)

print('Export functionality works correctly')
" && test_pass "Export functionality works" || test_fail "Export failed"

echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${RED}Failed:${NC} $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All tests passed! Package is ready.${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review and fix.${NC}"
    exit 1
fi
