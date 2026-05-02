@echo off
REM Build and publish CAJAL to PyPI
REM Requires: pip install build twine

echo Building CAJAL Python package...
cd /d "%~dp0\.."

if not exist dist mkdir dist

python -m build

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Build failed
    exit /b 1
)

echo ✅ Build successful!
echo.
echo To publish to PyPI, run:
echo   python -m twine upload dist/*
echo.
echo Or use the GitHub Action which publishes automatically on release.

pause
