# How to Update Package Version

If you need to publish a new version, follow these steps:

## Update Version Number

Update in **3 files**:

### 1. setup.py (line 12)
```python
version='1.0.1',  # Change from 1.0.0
```

### 2. pyproject.toml (line 7)
```toml
version = "1.0.1"  # Change from 1.0.0
```

### 3. rtsp_scanner/__init__.py (line 5)
```python
__version__ = "1.0.1"  # Change from 1.0.0
```

## Rebuild and Upload

```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info

# Build new version
python3 setup.py sdist bdist_wheel

# Check
python3 -m twine check dist/*

# Upload
python3 -m twine upload dist/*
```

## Version Numbering Guide

Follow [Semantic Versioning](https://semver.org/):

- **1.0.0 → 1.0.1** - Bug fix (patch)
- **1.0.0 → 1.1.0** - New feature (minor)
- **1.0.0 → 2.0.0** - Breaking change (major)

### Examples:

- Fixed a bug? → `1.0.1`
- Added new scan mode? → `1.1.0`
- Changed CLI commands? → `2.0.0`

## Quick Update Commands

```bash
# 1. Edit version in 3 files above

# 2. Rebuild
rm -rf dist && python3 setup.py sdist bdist_wheel

# 3. Upload
python3 -m twine upload dist/*
```
