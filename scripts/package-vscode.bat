@echo off
REM Package CAJAL VS Code Extension
REM Requires: npm install -g @vscode/vsce

cd /d "%~dp0\ecosystem\vscode-extension"

if not exist node_modules (
    echo Installing vsce...
    npm install -g @vscode/vsce
)

echo Packaging CAJAL VS Code Extension...
vsce package --out ..\..\dist\cajal-vscode.vsix

if %ERRORLEVEL% == 0 (
    echo ✅ Extension packaged successfully!
    echo Location: ..\..\dist\cajal-vscode.vsix
) else (
    echo ❌ Packaging failed
)

cd /d "%~dp0"
pause
