# PyPI Publishing Quick Start

This is a condensed guide to publish your RTSP Scanner package to PyPI.

## Prerequisites (One-Time Setup)

### 1. Create Accounts

**Test PyPI** (testing): https://test.pypi.org/account/register/
**PyPI** (production): https://pypi.org/account/register/

### 2. Install Tools

```bash
pip install --upgrade pip setuptools wheel twine
```

### 3. Update Your Info

Edit `setup.py`:
```python
author_email='YOUR_EMAIL@example.com',
url='https://github.com/YOUR_USERNAME/rtsp-scanner',
```

## Publishing Steps

### Quick Commands

```bash
# 1. Navigate to project
cd /Users/sanjayhona/workspace/SRE

# 2. Clean old builds
rm -rf build/ dist/ *.egg-info
find . -type d -name __pycache__ -exec rm -rf {} +

# 3. Build package
python3 setup.py sdist bdist_wheel

# 4. Check package
python3 -m twine check dist/*

# 5. Upload to Test PyPI (RECOMMENDED FIRST)
python3 -m twine upload --repository testpypi dist/*
# Username: Your Test PyPI username
# Password: Your Test PyPI password or token

# 6. Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps rtsp-scanner
rtsp-scanner --help

# 7. Upload to PyPI (if test was successful)
python3 -m twine upload dist/*
# Username: Your PyPI username
# Password: Your PyPI password or token

# 8. Verify
pip install rtsp-scanner
rtsp-scanner --help
```

## Using API Tokens (Recommended)

### Create Token

1. Log in to https://pypi.org
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Copy the token (starts with `pypi-`)

### Configure Token

Create `~/.pypirc`:

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_PYPI_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

Now you can upload without entering credentials:

```bash
python3 -m twine upload dist/*
```

## Pre-Publishing Checklist

Before running the commands above:

- [ ] Updated version number in `setup.py`
- [ ] Updated version in `pyproject.toml`
- [ ] Updated version in `rtsp_scanner/__init__.py`
- [ ] Updated `CHANGELOG.md`
- [ ] Updated author email in `setup.py`
- [ ] Updated GitHub URL in `setup.py`
- [ ] Committed and pushed to GitHub
- [ ] README.md is complete

## Common Issues

### "File already exists"
You can't replace a published version. Increment version number and rebuild.

### "Invalid authentication"
Use API token instead of password, or check credentials.

### "Package name already taken"
Choose a different name in setup.py (e.g., `my-rtsp-scanner`).

### Check if name is available
Visit: https://pypi.org/project/rtsp-scanner/
If 404, the name is available.

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- `1.0.0` → `1.0.1` - Bug fix
- `1.0.0` → `1.1.0` - New feature (backwards compatible)
- `1.0.0` → `2.0.0` - Breaking changes

Update in 3 places:
1. `setup.py` line 12: `version='1.0.1'`
2. `pyproject.toml` line 8: `version = "1.0.1"`
3. `rtsp_scanner/__init__.py` line 6: `__version__ = "1.0.1"`

## After Publishing

### Verify Your Package

Visit: https://pypi.org/project/rtsp-scanner/

Test installation:
```bash
pip install rtsp-scanner
rtsp-scanner --help
```

### Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Title: `Release 1.0.0`
5. Publish release

## Environment Variables (Alternative to .pypirc)

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
python3 -m twine upload dist/*
```

## Complete First-Time Workflow

```bash
# 1. Install twine
pip install twine

# 2. Update your information in setup.py
# Edit: author_email, url

# 3. Clean and build
cd /Users/sanjayhona/workspace/SRE
rm -rf build/ dist/ *.egg-info
python3 setup.py sdist bdist_wheel

# 4. Check
python3 -m twine check dist/*

# 5. Test on Test PyPI
python3 -m twine upload --repository testpypi dist/*
# Enter your Test PyPI credentials

# 6. Test install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps rtsp-scanner

# 7. If successful, upload to real PyPI
python3 -m twine upload dist/*
# Enter your PyPI credentials

# 8. Done! Anyone can now install with:
pip install rtsp-scanner
```

## Quick Reference Card

| Step | Command |
|------|---------|
| Clean | `rm -rf build/ dist/ *.egg-info` |
| Build | `python3 setup.py sdist bdist_wheel` |
| Check | `python3 -m twine check dist/*` |
| Test Upload | `python3 -m twine upload --repository testpypi dist/*` |
| Production Upload | `python3 -m twine upload dist/*` |
| Install | `pip install rtsp-scanner` |

## Resources

- Full Guide: See `PUBLISHING.md`
- PyPI: https://pypi.org
- Test PyPI: https://test.pypi.org
- Packaging Guide: https://packaging.python.org/

## Support

Having issues? Check `PUBLISHING.md` for detailed troubleshooting.

---

**Security Warning**: Never commit API tokens or `~/.pypirc` to git!

Add to `.gitignore`:
```
.pypirc
*.token
```
