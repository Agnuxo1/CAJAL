@echo off
cd /d D:\PROJECTS\CAJAL
echo ========================================
echo CAJAL-4B Training - Background Process
echo ========================================
echo Started: %date% %time%
echo.

start /B python scripts\train_cajal_4b.py ^
    --model-path "D:\PROJECTS\CAJAL\Modelos_originales\Qwen3.5-4B" ^
    --dataset "D:\PROJECTS\CAJAL\cajal_dataset.jsonl" ^
    --output-dir "D:\PROJECTS\CAJAL\outputs\CAJAL-4B" ^
    --output-name CAJAL-4B ^
    --epochs 3 ^
    --batch-size 2 ^
    --grad-accum 4 ^
    --lr 2e-4 ^
    --max-seq-length 2048 ^
    --lora-r 16 ^
    --lora-alpha 32 ^
    --use-thinking ^
    > "training_4B_background.log" 2>&1

echo Training process started in background.
echo PID: %ERRORLEVEL%
echo Log: D:\PROJECTS\CAJAL\training_4B_background.log
echo.
echo To monitor progress: type training_4B_background.log
echo To check if running: tasklist | findstr python