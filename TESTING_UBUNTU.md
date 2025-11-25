# Testing on Ubuntu Linux

Before publishing to PyPI, test your package on Ubuntu/Linux to ensure cross-platform compatibility.

## Quick Test on Ubuntu

### Option 1: Using Docker (Fastest)

Test on Ubuntu without needing a real Ubuntu machine:

```bash
# Pull Ubuntu image
docker pull ubuntu:22.04

# Run interactive container
docker run -it -v $(pwd):/app ubuntu:22.04 bash

# Inside container:
cd /app
apt update
apt install -y python3 python3-pip
pip3 install dist/rtsp_network_scanner-1.0.0-py3-none-any.whl
rtsp-scanner --help
python3 test_basic.py
```

### Option 2: Ubuntu VM or Server

If you have access to Ubuntu:

```bash
# Copy package to Ubuntu
scp dist/rtsp_network_scanner-1.0.0-py3-none-any.whl user@ubuntu-server:~
scp test_basic.py user@ubuntu-server:~

# SSH to Ubuntu
ssh user@ubuntu-server

# Install and test
pip3 install rtsp_network_scanner-1.0.0-py3-none-any.whl
rtsp-scanner --help
python3 test_basic.py
```

### Option 3: GitHub Actions (Automated)

Create `.github/workflows/test.yml`:

```yaml
name: Test Package

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.7', '3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install package
      run: |
        pip install dist/rtsp_network_scanner-1.0.0-py3-none-any.whl

    - name: Run tests
      run: |
        python test_basic.py

    - name: Test CLI
      run: |
        rtsp-scanner --help
        rtsp-scanner validate-url rtsp://test.com:554/stream
```

## Manual Testing on Ubuntu

### 1. Basic Installation Test

```bash
pip3 install dist/rtsp_network_scanner-1.0.0-py3-none-any.whl
```

Expected output:
```
Successfully installed rtsp-network-scanner-1.0.0
```

### 2. CLI Test

```bash
rtsp-scanner --help
```

Expected: Help text displays

### 3. Validate URL Test

```bash
rtsp-scanner validate-url rtsp://192.168.1.100:554/stream
```

Expected output:
```
URL: rtsp://192.168.1.100:554/stream
Valid: True
Message: Valid RTSP URL
```

### 4. Python Import Test

```bash
python3 -c "from rtsp_scanner.core.port_scanner import PortScanner; print('OK')"
```

Expected output: `OK`

### 5. Run Full Test Suite

```bash
python3 test_basic.py
```

Expected: All 10 tests pass

### 6. Network Scan Test (Requires Network)

```bash
# Test on localhost (safe)
rtsp-scanner scan-ports 127.0.0.1 --ports 80 443 --timeout 1
```

Expected: Scans complete without errors

## Docker Test Commands (Copy & Paste)

Complete Docker test in one command:

```bash
docker run --rm -v $(pwd):/app ubuntu:22.04 bash -c "
cd /app && \
apt update -qq && \
apt install -y python3 python3-pip -qq && \
pip3 install -q dist/rtsp_network_scanner-1.0.0-py3-none-any.whl && \
echo '=== Testing CLI ===' && \
rtsp-scanner --help && \
echo && \
echo '=== Testing URL Validation ===' && \
rtsp-scanner validate-url rtsp://test.com:554/stream && \
echo && \
echo '=== Running Test Suite ===' && \
python3 test_basic.py
"
```

## What to Check

### ✓ Cross-Platform Compatibility

- [ ] Package installs on Ubuntu
- [ ] CLI commands work
- [ ] No macOS-specific code issues
- [ ] File paths work (/ vs \)
- [ ] Python 3.7+ compatibility

### ✓ Dependencies

- [ ] No external dependencies (uses stdlib only)
- [ ] All imports work
- [ ] No missing modules

### ✓ Functionality

- [ ] Port scanning works
- [ ] URL validation works
- [ ] Logger creates files
- [ ] Export to JSON/CSV works
- [ ] All CLI commands execute

## Common Issues on Linux

### Issue: Permission Denied

```bash
# Fix:
chmod +x test_basic.py
```

### Issue: Python 3 not found

```bash
# Install Python 3
sudo apt update
sudo apt install python3 python3-pip
```

### Issue: rtsp-scanner command not found

```bash
# Add to PATH
export PATH="$PATH:$HOME/.local/bin"

# Or use python -m
python3 -m rtsp_scanner.cli --help
```

## Quick Ubuntu Test Checklist

```bash
# 1. Install
pip3 install dist/rtsp_network_scanner-1.0.0-py3-none-any.whl

# 2. Test help
rtsp-scanner --help

# 3. Test validation
rtsp-scanner validate-url rtsp://test.com:554/stream

# 4. Run tests
python3 test_basic.py

# 5. Uninstall
pip3 uninstall rtsp-network-scanner -y
```

## Testing on Different Python Versions

```bash
# Python 3.7
docker run --rm -v $(pwd):/app python:3.7 bash -c \
  "cd /app && pip install dist/*.whl && python test_basic.py"

# Python 3.8
docker run --rm -v $(pwd):/app python:3.8 bash -c \
  "cd /app && pip install dist/*.whl && python test_basic.py"

# Python 3.9
docker run --rm -v $(pwd):/app python:3.9 bash -c \
  "cd /app && pip install dist/*.whl && python test_basic.py"

# Python 3.10
docker run --rm -v $(pwd):/app python:3.10 bash -c \
  "cd /app && pip install dist/*.whl && python test_basic.py"

# Python 3.11
docker run --rm -v $(pwd):/app python:3.11 bash -c \
  "cd /app && pip install dist/*.whl && python test_basic.py"
```

## Results

After testing, you should see:
- ✓ Package installs successfully
- ✓ CLI works on Linux
- ✓ All 10 tests pass
- ✓ No compatibility issues
- ✓ Ready to publish!

## If Tests Fail

1. Check the error message
2. Fix the issue
3. Rebuild: `rm -rf dist && python3 setup.py sdist bdist_wheel`
4. Re-test

## Ready to Publish?

If all tests pass on both macOS and Ubuntu:

```bash
python3 -m twine upload dist/*
```

---

**Note**: The package has been tested on macOS already and passed all 10 tests. Docker testing on Ubuntu is recommended but optional since the package uses only Python standard library.
