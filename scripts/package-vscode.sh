#!/bin/bash
# Package CAJAL VS Code Extension
# Requires: npm install -g @vscode/vsce

set -e

cd "$(dirname "$0")/../ecosystem/vscode-extension"

if ! command -v vsce &> /dev/null; then
    echo "Installing vsce..."
    npm install -g @vscode/vsce
fi

echo "Packaging CAJAL VS Code Extension..."
mkdir -p ../../dist
vsce package --out ../../dist/cajal-vscode.vsix

echo "✅ Extension packaged successfully!"
echo "Location: dist/cajal-vscode.vsix"
