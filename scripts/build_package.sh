#!/bin/bash
# Build script for RTSP Scanner package

set -e

echo "=========================================="
echo "RTSP Scanner - Package Build Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")/.."

echo "Step 1: Cleaning old build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✓${NC} Cleaned"
echo ""

echo "Step 2: Building source distribution and wheel..."
python3 setup.py sdist bdist_wheel
echo -e "${GREEN}✓${NC} Built"
echo ""

echo "Step 3: Checking package with twine..."
python3 -m twine check dist/*
echo -e "${GREEN}✓${NC} Package validation passed"
echo ""

echo "Step 4: Package information..."
echo "----------------------------------------"
ls -lh dist/
echo "----------------------------------------"
echo ""

# Extract version
VERSION=$(grep "version=" setup.py | head -1 | sed "s/.*version='\(.*\)'.*/\1/")

echo -e "${GREEN}Build completed successfully!${NC}"
echo ""
echo "Package: rtsp-scanner v$VERSION"
echo ""
echo "Built files:"
echo "  - dist/rtsp-scanner-$VERSION.tar.gz (source distribution)"
echo "  - dist/rtsp_scanner-$VERSION-py3-none-any.whl (wheel)"
echo ""
echo "Next steps:"
echo ""
echo "  Test on Test PyPI:"
echo "    python3 -m twine upload --repository testpypi dist/*"
echo ""
echo "  Test installation:"
echo "    pip install --index-url https://test.pypi.org/simple/ --no-deps rtsp-scanner"
echo ""
echo "  Upload to PyPI:"
echo "    python3 -m twine upload dist/*"
echo ""
