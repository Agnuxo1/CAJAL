@echo off
REM CAJAL-9B Training - Resume from checkpoint
REM Runs training and auto-resumes from latest checkpoint

cd /d "D:\PROJECTS\CAJAL"

echo ============================================
echo   CAJAL-9B Training (Auto-Resume)
echo   Resuming from checkpoint-500
echo ============================================
echo.

python scripts\train_cajal_9b.py

echo.
if errorlevel 1 (
    echo [ERROR] Training failed with error code %errorlevel%
) else (
    echo Training completed successfully!
)
pause