#!/bin/bash
# Build script for Deep Freeze

set -e

echo "Building Deep Freeze..."
echo "======================="

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# Run tests
echo ""
echo "Running tests..."
python -m pytest tests/ -v --cov=deepfreeze

# Check code quality
echo ""
echo "Checking code quality..."
black --check src tests || (echo "Run 'black src tests' to format code" && exit 1)
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503

# Build package
echo ""
echo "Building package..."
python -m build

echo ""
echo "Build complete! Package ready in dist/"
ls -lh dist/
