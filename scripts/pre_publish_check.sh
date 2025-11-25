#!/bin/bash
# Pre-publish checklist script for RTSP Scanner

set -e

echo "=========================================="
echo "RTSP Scanner - Pre-Publish Checklist"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN++))
}

echo "Checking prerequisites..."
echo ""

# Check if twine is installed
if command -v twine &> /dev/null; then
    check_pass "Twine is installed"
else
    check_fail "Twine is not installed (run: pip install twine)"
fi

# Check if we're in the right directory
if [ -f "setup.py" ] && [ -d "rtsp_scanner" ]; then
    check_pass "In correct directory"
else
    check_fail "Not in project root directory"
    exit 1
fi

echo ""
echo "Checking files..."
echo ""

# Check required files exist
for file in setup.py pyproject.toml README.md LICENSE MANIFEST.in CHANGELOG.md; do
    if [ -f "$file" ]; then
        check_pass "$file exists"
    else
        check_fail "$file is missing"
    fi
done

echo ""
echo "Checking version consistency..."
echo ""

# Extract versions
SETUP_VERSION=$(grep "version=" setup.py | head -1 | sed "s/.*version='\(.*\)'.*/\1/")
PYPROJECT_VERSION=$(grep "^version = " pyproject.toml | sed 's/.*version = "\(.*\)".*/\1/')
INIT_VERSION=$(grep "__version__ = " rtsp_scanner/__init__.py | sed 's/.*__version__ = "\(.*\)".*/\1/')

echo "  setup.py: $SETUP_VERSION"
echo "  pyproject.toml: $PYPROJECT_VERSION"
echo "  __init__.py: $INIT_VERSION"
echo ""

if [ "$SETUP_VERSION" = "$PYPROJECT_VERSION" ] && [ "$SETUP_VERSION" = "$INIT_VERSION" ]; then
    check_pass "Version numbers are consistent ($SETUP_VERSION)"
else
    check_fail "Version numbers are inconsistent!"
fi

echo ""
echo "Checking configuration..."
echo ""

# Check if placeholder values are updated
if grep -q "your.email@example.com" setup.py; then
    check_warn "Author email still contains placeholder (update in setup.py)"
else
    check_pass "Author email is configured"
fi

if grep -q "yourusername" setup.py; then
    check_warn "GitHub URL still contains placeholder (update in setup.py)"
else
    check_pass "GitHub URL is configured"
fi

echo ""
echo "Checking git status..."
echo ""

if [ -d ".git" ]; then
    if git diff-index --quiet HEAD --; then
        check_pass "No uncommitted changes"
    else
        check_warn "You have uncommitted changes"
    fi

    # Check if we have a remote
    if git remote -v | grep -q "origin"; then
        check_pass "Git remote is configured"
    else
        check_warn "No git remote configured"
    fi
else
    check_warn "Not a git repository"
fi

echo ""
echo "Checking build artifacts..."
echo ""

if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    check_warn "dist/ directory exists (will be cleaned during build)"
fi

if [ -d "build" ]; then
    check_warn "build/ directory exists (will be cleaned during build)"
fi

echo ""
echo "Checking Python syntax..."
echo ""

# Check Python files for syntax errors
find rtsp_scanner -name "*.py" -exec python3 -m py_compile {} \; 2>&1
if [ $? -eq 0 ]; then
    check_pass "All Python files have valid syntax"
else
    check_fail "Python syntax errors found"
fi

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo -e "${RED}Failed:${NC} $FAIL"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}Please fix the failed checks before publishing!${NC}"
    exit 1
elif [ $WARN -gt 0 ]; then
    echo -e "${YELLOW}There are warnings. Review them before publishing.${NC}"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}All checks passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Clean and build: ./scripts/build_package.sh"
echo "  2. Test upload: python3 -m twine upload --repository testpypi dist/*"
echo "  3. Production upload: python3 -m twine upload dist/*"
echo ""
