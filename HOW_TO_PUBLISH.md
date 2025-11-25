# How to Publish RTSP Scanner to PyPI

## TL;DR - Quick Publishing Commands

```bash
# 1. Install tools
pip3 install twine

# 2. Clean and build
rm -rf build/ dist/ *.egg-info
python3 setup.py sdist bdist_wheel

# 3. Check
python3 -m twine check dist/*

# 4. Upload
python3 -m twine upload dist/*
```

## Step-by-Step Guide

### 1. One-Time Setup (First Time Only)

#### Create PyPI Account
Go to https://pypi.org/account/register/ and create an account.

#### Install Publishing Tools
```bash
pip3 install --upgrade twine wheel setuptools
```

#### Update Package Info
Edit `setup.py` and replace:
- `author_email='your.email@example.com'` with your email
- `url='https://github.com/yourusername/rtsp-scanner'` with your GitHub repo

### 2. Prepare for Publishing

#### Check Version Number
Make sure these 3 files have the same version:
- `setup.py` (line 12): `version='1.0.0'`
- `pyproject.toml` (line 8): `version = "1.0.0"`
- `rtsp_scanner/__init__.py` (line 6): `__version__ = "1.0.0"`

#### Update CHANGELOG.md
Document what's new in this version.

### 3. Build the Package

```bash
# Navigate to project
cd /Users/sanjayhona/workspace/SRE

# Clean old builds
rm -rf build/ dist/ *.egg-info

# Build
python3 setup.py sdist bdist_wheel
```

This creates:
- `dist/rtsp-scanner-1.0.0.tar.gz` - Source package
- `dist/rtsp_scanner-1.0.0-py3-none-any.whl` - Wheel package

### 4. Test the Package

```bash
# Validate package
python3 -m twine check dist/*
```

Should show:
```
Checking dist/rtsp_scanner-1.0.0-py3-none-any.whl: PASSED
Checking dist/rtsp-scanner-1.0.0.tar.gz: PASSED
```

### 5. Upload to PyPI

```bash
python3 -m twine upload dist/*
```

You'll be asked for:
- **Username**: Your PyPI username
- **Password**: Your PyPI password

### 6. Verify Publication

Visit: https://pypi.org/project/rtsp-scanner/

Test installation:
```bash
pip install rtsp-scanner
rtsp-scanner --help
```

## Using Test PyPI First (Recommended)

Always test on Test PyPI before uploading to the real PyPI!

### 1. Create Test PyPI Account
https://test.pypi.org/account/register/

### 2. Upload to Test PyPI
```bash
python3 -m twine upload --repository testpypi dist/*
```

### 3. Test Installation
```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps rtsp-scanner
rtsp-scanner --help
```

### 4. If Successful, Upload to Real PyPI
```bash
python3 -m twine upload dist/*
```

## Using API Tokens (More Secure)

### Create Token
1. Log in to https://pypi.org
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Give it a name: "rtsp-scanner-upload"
5. Copy the token (starts with `pypi-`)

### Save Token
Create `~/.pypirc`:

```bash
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

Now you can upload without entering password:
```bash
python3 -m twine upload dist/*
```

## Complete Workflow Example

```bash
# 1. Update version numbers (if new release)
# Edit: setup.py, pyproject.toml, __init__.py

# 2. Update CHANGELOG.md

# 3. Commit changes
git add .
git commit -m "Release v1.0.0"
git push

# 4. Clean and build
cd /Users/sanjayhona/workspace/SRE
rm -rf build/ dist/ *.egg-info
python3 setup.py sdist bdist_wheel

# 5. Check package
python3 -m twine check dist/*

# 6. Test on Test PyPI
python3 -m twine upload --repository testpypi dist/*

# 7. Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps rtsp-scanner
rtsp-scanner --help

# 8. Upload to production PyPI
python3 -m twine upload dist/*

# 9. Test final installation
pip install rtsp-scanner
rtsp-scanner --help

# 10. Create GitHub release
# Go to GitHub → Releases → Create new release → v1.0.0
```

## Troubleshooting

### "twine: command not found"

Install twine:
```bash
pip3 install twine

# Or if that doesn't work
python3 -m pip install twine
```

### "File already exists on PyPI"

You cannot upload the same version twice. You must:
1. Increment version number in all 3 places
2. Rebuild: `rm -rf dist/ && python3 setup.py sdist bdist_wheel`
3. Re-upload: `python3 -m twine upload dist/*`

### "Invalid username or password"

Use an API token instead of password (see "Using API Tokens" section above).

### "Package name already taken"

Someone else has that name. Change package name in `setup.py`:
```python
name='my-rtsp-scanner',  # or any other unique name
```

### Check if Name is Available

Visit: https://pypi.org/project/rtsp-scanner/

If you see "404 Not Found", the name is available.

## Updating Your Package

When releasing a new version:

1. **Update version** in 3 files (setup.py, pyproject.toml, __init__.py)
2. **Update CHANGELOG.md**
3. **Commit and push** to GitHub
4. **Clean and rebuild**: `rm -rf dist/ && python3 setup.py sdist bdist_wheel`
5. **Check**: `python3 -m twine check dist/*`
6. **Upload**: `python3 -m twine upload dist/*`

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **1.0.0 → 1.0.1** - Bug fixes only
- **1.0.0 → 1.1.0** - New features (backwards compatible)
- **1.0.0 → 2.0.0** - Breaking changes

## After Publishing

### Share Your Package

Tell the world:
```
pip install rtsp-scanner
```

### Monitor Downloads

Check stats at: https://pypistats.org/packages/rtsp-scanner

### Update Documentation

Make sure your GitHub README shows the correct install command.

## Automated Publishing (Advanced)

For automatic publishing when you create a GitHub release, see the "GitHub Actions" section in `PUBLISHING.md`.

## Pre-Publishing Checklist

Use this checklist before each publish:

```bash
# Run automated checks
./scripts/pre_publish_check.sh

# Manual checks:
☐ Version numbers updated and consistent
☐ CHANGELOG.md updated
☐ README.md is current
☐ All tests pass
☐ Author email updated in setup.py
☐ GitHub URLs updated in setup.py
☐ LICENSE file present
☐ Committed all changes to git
☐ Package builds without errors
☐ `twine check` passes
```

## Resources

- **Detailed Guide**: See `PUBLISHING.md` for comprehensive documentation
- **Quick Reference**: See `PYPI_QUICKSTART.md` for command cheat sheet
- **PyPI Homepage**: https://pypi.org
- **Test PyPI**: https://test.pypi.org
- **Python Packaging Guide**: https://packaging.python.org/

## Need Help?

1. Check `PUBLISHING.md` for detailed troubleshooting
2. Visit https://packaging.python.org/
3. Ask on https://discuss.python.org/c/packaging/

---

## Quick Command Reference

| Action | Command |
|--------|---------|
| Install tools | `pip3 install twine` |
| Clean | `rm -rf build/ dist/ *.egg-info` |
| Build | `python3 setup.py sdist bdist_wheel` |
| Check | `python3 -m twine check dist/*` |
| Test Upload | `python3 -m twine upload --repository testpypi dist/*` |
| Real Upload | `python3 -m twine upload dist/*` |
| Install | `pip install rtsp-scanner` |

---

**Ready to publish?** Start with the TL;DR commands at the top of this file!
