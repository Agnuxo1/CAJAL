#!/bin/bash
# Publish CAJAL VS Code extension to OpenVSX
# Requires: npx ovsx (install: npm install -g ovsx)
# Get token from: https://open-vsx.org/

cd "$(dirname "$0")/extensions/vscode"

# Use the already-built VSIX
npx ovsx publish cajal-p2pclaw-vscode-1.0.0.vsix -p "$OPENVSX_TOKEN"

echo "✅ Published to OpenVSX!"
echo "Check: https://open-vsx.org/extension/agnuxo1/cajal-p2pclaw-vscode"
