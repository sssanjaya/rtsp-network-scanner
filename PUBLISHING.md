# Publishing RTSP Scanner to PyPI

This guide will walk you through publishing the RTSP Scanner package to PyPI (Python Package Index) so others can install it with `pip install rtsp-scanner`.

## Prerequisites

### 1. Create PyPI Account

You need accounts on both Test PyPI (for testing) and PyPI (for production):

**Test PyPI** (for testing uploads):
- Visit: https://test.pypi.org/account/register/
- Create an account and verify your email

**PyPI** (for production):
- Visit: https://pypi.org/account/register/
- Create an account and verify your email

### 2. Install Required Tools

```bash
pip install --upgrade pip setuptools wheel twine
```

### 3. Update Package Information

Before publishing, update these files with your actual information:

#### In `setup.py`:
```python
author_email='your.email@example.com',  # Change this
url='https://github.com/YOUR_USERNAME/rtsp-scanner',  # Change this
```

#### In `pyproject.toml`:
```toml
[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/rtsp-scanner"
```

## Step-by-Step Publishing Guide

### Step 1: Prepare the Package

#### 1.1 Clean Previous Builds

```bash
cd /Users/sanjayhona/workspace/SRE

# Remove old build artifacts
rm -rf build/ dist/ *.egg-info

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

#### 1.2 Update Version Number

If this is a new release, update the version in:
- `setup.py` → `version='1.0.0'`
- `pyproject.toml` → `version = "1.0.0"`
- `rtsp_scanner/__init__.py` → `__version__ = "1.0.0"`

Version format: `MAJOR.MINOR.PATCH` (e.g., 1.0.0, 1.0.1, 1.1.0, 2.0.0)

### Step 2: Build the Package

```bash
# Build source distribution and wheel
python3 setup.py sdist bdist_wheel
```

This creates:
- `dist/rtsp-scanner-1.0.0.tar.gz` - Source distribution
- `dist/rtsp_scanner-1.0.0-py3-none-any.whl` - Wheel package

### Step 3: Check the Package

Validate the package before uploading:

```bash
twine check dist/*
```

Expected output:
```
Checking dist/rtsp-scanner-1.0.0.tar.gz: PASSED
Checking dist/rtsp_scanner-1.0.0-py3-none-any.whl: PASSED
```

If you see any errors, fix them before proceeding.

### Step 4: Test Upload to Test PyPI (RECOMMENDED)

Always test on Test PyPI first!

#### 4.1 Upload to Test PyPI

```bash
twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: Your Test PyPI username
- Password: Your Test PyPI password (or API token)

#### 4.2 Test Installation from Test PyPI

```bash
# Create a test virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps rtsp-scanner

# Test the installation
rtsp-scanner --help
python3 -c "from rtsp_scanner import PortScanner; print('Import successful!')"

# Clean up
deactivate
rm -rf test_env
```

### Step 5: Upload to Production PyPI

If testing was successful, upload to the real PyPI:

```bash
twine upload dist/*
```

You'll be prompted for:
- Username: Your PyPI username
- Password: Your PyPI password (or API token)

### Step 6: Verify Publication

Visit your package page:
- https://pypi.org/project/rtsp-scanner/

Test installation:
```bash
pip install rtsp-scanner
rtsp-scanner --help
```

## Using API Tokens (Recommended)

API tokens are more secure than passwords.

### Creating PyPI API Token

1. Log in to https://pypi.org
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Give it a name (e.g., "rtsp-scanner-upload")
5. Select scope: "Entire account" or specific project
6. Copy the token (starts with `pypi-`)

### Using Token for Upload

Option 1: Configure in `~/.pypirc`:

```bash
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

Option 2: Use environment variables:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
twine upload dist/*
```

## Complete Publishing Workflow

Here's the complete workflow from start to finish:

```bash
# 1. Navigate to project
cd /Users/sanjayhona/workspace/SRE

# 2. Update version numbers if needed
# Edit setup.py, pyproject.toml, and __init__.py

# 3. Clean old builds
rm -rf build/ dist/ *.egg-info
find . -type d -name __pycache__ -exec rm -rf {} +

# 4. Build the package
python3 setup.py sdist bdist_wheel

# 5. Check the package
twine check dist/*

# 6. Upload to Test PyPI (recommended first)
twine upload --repository testpypi dist/*

# 7. Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps rtsp-scanner

# 8. If all tests pass, upload to PyPI
twine upload dist/*

# 9. Verify
pip install rtsp-scanner
rtsp-scanner --help
```

## Publishing Checklist

Before publishing, ensure:

- [ ] Version number is updated
- [ ] README.md is up to date
- [ ] CHANGELOG.md is updated (if you have one)
- [ ] All tests pass
- [ ] Documentation is current
- [ ] GitHub repository URL is correct in setup.py
- [ ] Author email is correct in setup.py
- [ ] LICENSE file exists
- [ ] .gitignore excludes build artifacts
- [ ] Package builds without errors
- [ ] `twine check` passes
- [ ] Tested on Test PyPI first
- [ ] Committed and pushed to GitHub

## Updating an Existing Package

When releasing a new version:

1. **Update version numbers** (setup.py, pyproject.toml, __init__.py)
2. **Update CHANGELOG.md** with changes
3. **Clean and rebuild**: `rm -rf dist/ && python3 setup.py sdist bdist_wheel`
4. **Check**: `twine check dist/*`
5. **Upload**: `twine upload dist/*`

## Troubleshooting

### Issue: "File already exists"

You tried to upload a version that already exists. You cannot replace a published version.

**Solution**: Increment the version number and rebuild.

### Issue: "Invalid authentication"

Your username/password or token is incorrect.

**Solution**:
- Verify credentials
- Use API token instead of password
- Check `~/.pypirc` configuration

### Issue: "Package name already taken"

Someone else already published a package with this name.

**Solution**:
- Choose a different name in setup.py
- Add a prefix/suffix (e.g., `rtsp-scanner-plus`, `my-rtsp-scanner`)

### Issue: "Long description has syntax errors"

Your README.md has formatting issues.

**Solution**:
- Check README.md syntax
- Ensure it's valid Markdown
- Run: `python3 -m readme_renderer README.md`

## Package Name Considerations

### Check if Name is Available

Before publishing, check if the name is available:

```bash
pip search rtsp-scanner
```

Or visit: https://pypi.org/project/rtsp-scanner/

If the name is taken, consider alternatives:
- `rtsp-network-scanner`
- `rtsp-stream-scanner`
- `rtspscanner`
- Add your username prefix: `yourname-rtsp-scanner`

## GitHub Integration

### 1. Create GitHub Repository

```bash
# Initialize git (if not already)
git init

# Add files
git add .
git commit -m "Initial commit - RTSP Scanner v1.0.0"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/rtsp-scanner.git
git branch -M main
git push -u origin main
```

### 2. Create GitHub Release

After publishing to PyPI:

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Title: `Release 1.0.0`
5. Description: Paste changelog
6. Upload the dist files (optional)
7. Click "Publish release"

### 3. Update Package URLs

After creating the GitHub repo, update setup.py with the real URL:

```python
url='https://github.com/YOUR_USERNAME/rtsp-scanner',
project_urls={
    'Bug Reports': 'https://github.com/YOUR_USERNAME/rtsp-scanner/issues',
    'Source': 'https://github.com/YOUR_USERNAME/rtsp-scanner',
    'Documentation': 'https://github.com/YOUR_USERNAME/rtsp-scanner#readme',
},
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install setuptools wheel twine
    - name: Build package
      run: python setup.py sdist bdist_wheel
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add your PyPI token to GitHub Secrets:
- Go to repository Settings → Secrets → Actions
- Add secret named `PYPI_API_TOKEN`
- Paste your PyPI API token

## Resources

- **PyPI**: https://pypi.org
- **Test PyPI**: https://test.pypi.org
- **Packaging Guide**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **Setup.py Guide**: https://setuptools.pypa.io/

## Support

If you encounter issues:
1. Check the PyPI packaging guide
2. Search for the error message
3. Ask on https://discuss.python.org/c/packaging/

## Quick Reference Card

```bash
# Install tools
pip install twine wheel

# Clean
rm -rf build dist *.egg-info

# Build
python3 setup.py sdist bdist_wheel

# Check
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install and test
pip install rtsp-scanner
rtsp-scanner --help
```

---

**Important Security Note**: Never commit `~/.pypirc` or any files containing API tokens to version control!
