#!/usr/bin/env bash
# CAJAL CLI - PyPI Publication Script
# Usage: bash publish-pypi.sh

set -e

PACKAGE_DIR="$(cd "$(dirname "$0")/../pypi-package" && pwd)"
DIST_DIR="$PACKAGE_DIR/dist"

echo "========================================"
echo "  CAJAL CLI - PyPI Publisher"
echo "  P2PCLAW Lab, Zurich"
echo "========================================"

# Check prerequisites
echo ""
echo "[1/6] Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

if ! python3 -c "import build" 2>/dev/null; then
    echo "Installing build tools..."
    python3 -m pip install --upgrade build twine setuptools wheel
fi

# Clean previous builds
echo ""
echo "[2/6] Cleaning previous builds..."
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# Build package
echo ""
echo "[3/6] Building package..."
cd "$PACKAGE_DIR"
python3 -m build

# Verify builds
echo ""
echo "[4/6] Verifying builds..."
if [ ! -f "$DIST_DIR"/*.whl ]; then
    echo "ERROR: Wheel file not found"
    exit 1
fi
if [ ! -f "$DIST_DIR"/*.tar.gz ]; then
    echo "ERROR: Source distribution not found"
    exit 1
fi

echo "Built files:"
ls -lh "$DIST_DIR"

# Check with twine
echo ""
echo "[5/6] Checking with twine..."
python3 -m twine check "$DIST_DIR"/*

# Upload to PyPI
echo ""
echo "[6/6] Uploading to PyPI..."
echo ""
echo "Using PyPI token authentication..."

# Set token from environment or prompt
if [ -z "$PYPI_TOKEN" ]; then
    echo ""
    read -p "Enter PyPI API token: " PYPI_TOKEN
    export PYPI_TOKEN
fi

python3 -m twine upload \
    --username "__token__" \
    --password "$PYPI_TOKEN" \
    "$DIST_DIR"/*

echo ""
echo "========================================"
echo "  Published successfully!"
echo "  pip install cajal-cli"
echo "========================================"
