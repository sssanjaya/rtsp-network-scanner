# Pre-Publish Checklist

Complete this checklist before uploading to PyPI.

## ✅ Tests Completed

### macOS Tests (Current System)
- [x] All modules import successfully
- [x] URL validation works
- [x] URL parsing works
- [x] PortScanner initialization
- [x] ChannelScanner initialization
- [x] Logger functionality
- [x] OutputFormatter works
- [x] URL generation
- [x] Export to JSON/CSV
- [x] Package metadata correct
- [x] **Result: 10/10 tests passed ✓**

### Ubuntu/Linux Tests (Optional but Recommended)
- [ ] Tested on Ubuntu (see TESTING_UBUNTU.md)
- [ ] Docker test completed
- [ ] CLI works on Linux

## ✅ Package Quality

### Code Quality
- [x] No syntax errors
- [x] All imports work
- [x] No hardcoded paths
- [x] Uses stdlib only (no external deps)
- [x] Python 3.7+ compatible

### Configuration
- [x] Package name: `rtsp-network-scanner`
- [x] Version: `1.0.0`
- [x] Author email: `contact@sanjayhona.com.np`
- [x] GitHub URL: `https://github.com/sssanjaya/rtsp-network-scanner`
- [x] Description: Clear and concise
- [x] Keywords: Relevant and searchable

### Documentation
- [x] README.md: Clear and simple
- [x] LICENSE file exists
- [x] CHANGELOG.md created
- [x] Examples provided
- [x] Installation instructions
- [x] Usage examples

### Package Files
- [x] setup.py configured
- [x] pyproject.toml configured
- [x] MANIFEST.in exists
- [x] .gitignore configured
- [x] Package builds without errors
- [x] Both tar.gz and wheel created

## ✅ Validation

### Twine Check
- [x] `twine check dist/*` passes
- [x] No warnings or errors

### Manual Testing
```bash
# Run this to verify:
python3 test_basic.py
```
- [x] All tests pass

### CLI Testing
```bash
# Test these commands:
rtsp-scanner --help                              # Works ✓
rtsp-scanner validate-url rtsp://test.com:554/   # Works ✓
```

## ✅ Security

- [x] No hardcoded credentials
- [x] No API keys in code
- [x] Security warnings in README
- [x] Only authorized use mentioned

## ✅ Pre-Upload

### Final Checks
- [x] Version numbers consistent (setup.py, pyproject.toml, __init__.py)
- [x] All placeholder URLs replaced
- [x] Author info correct
- [x] LICENSE file included
- [x] No sensitive data in package

### Build Clean
```bash
rm -rf build/ dist/ *.egg-info
python3 setup.py sdist bdist_wheel
python3 -m twine check dist/*
```
- [x] Clean build successful
- [x] Validation passed

## 📊 Test Results Summary

```
Test Date: 2025-11-25
Python Version: 3.9.6
Platform: macOS (Darwin 24.6.0)

Results:
- Imports: ✓
- URL Validation: ✓
- URL Parsing: ✓
- PortScanner: ✓
- ChannelScanner: ✓
- Logger: ✓
- OutputFormatter: ✓
- URL Generation: ✓
- Exports: ✓
- Metadata: ✓

Total: 10/10 PASSED
```

## 🚀 Ready to Publish?

If all items above are checked:

```bash
# Upload to PyPI
python3 -m twine upload dist/*
```

## 📝 Post-Publish

After successful upload:

- [ ] Verify package on PyPI: https://pypi.org/project/rtsp-network-scanner/
- [ ] Test installation: `pip install rtsp-network-scanner`
- [ ] Create GitHub release (tag: v1.0.0)
- [ ] Update repository README with PyPI badge
- [ ] Share on social media/communities

## 🔗 Important Links

- **PyPI**: https://pypi.org/project/rtsp-network-scanner/
- **GitHub**: https://github.com/sssanjaya/rtsp-network-scanner
- **Issues**: https://github.com/sssanjaya/rtsp-network-scanner/issues

## ⚠️ Final Reminder

Once published to PyPI:
- Cannot delete or replace version 1.0.0
- Cannot reuse version number
- Must increment version for any changes
- Package becomes public and permanent

**Double-check everything before uploading!**

---

## Current Status

✅ **READY TO PUBLISH**

All tests passed. Package validated. No bugs found.

**Next step**: Run `python3 -m twine upload dist/*`
