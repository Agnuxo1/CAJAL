#!/bin/bash
# Publish CAJAL npm package
# Run this after logging into npm: npm login

cd "$(dirname "$0")/extensions/npm" || exit 1

# Build first
npm install
npm run build

# Publish to npm (public access for scoped or unscoped packages)
npm publish --access public

echo "✅ Published to npm!"
echo "Check: https://www.npmjs.com/package/cajal-p2pclaw"
