@echo off
REM CAJAL-9B Training Launcher
REM Optimized for Windows 11 + RTX 3090 24GB

echo ============================================
echo   CAJAL-9B Training
echo   Qwen3.5-9B + LoRA Agent Workflow
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')" 2>nul | findstr "True" >nul
if errorlevel 1 (
    echo [WARNING] CUDA may not be available. Training will be very slow on CPU.
    echo.
)

REM Check VRAM
python -c "import torch; print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB')" 2>nul

echo.
echo Model: Qwen3.5-9B (19GB safetensors)
echo Dataset: datasets/cajal_9b_agent_dataset.jsonl
echo Output: outputs/CAJAL-9B/
echo.
echo Hyperparameters:
echo   Epochs: 5
echo   LoRA r=32, alpha=64
echo   Learning rate: 1e-4
echo   Batch size: 1 (grad accum: 4)
echo   Max seq length: 4096
echo   Quantization: 4-bit NF4
echo.
echo Estimated training time: 15-25 hours
echo.

set /p confirm="Start training? (Y/n): "
if /I not "%confirm%"=="Y" if not "%confirm%"=="" (
    echo Cancelled.
    exit /b 0
)

cd /d "D:\PROJECTS\CAJAL"

echo.
echo [1/1] Starting CAJAL-9B training...
python scripts\train_cajal_9b.py

echo.
echo ============================================
echo   Training Complete
echo ============================================
echo Next steps:
echo   1. Merge adapters: python scripts\merge_cajal_9b.py
echo   2. Convert to GGUF: python convert_hf_to_gguf.py
echo   3. Create Ollama model: ollama create cajal-9b -f outputs\CAJAL-9B\Modelfile
echo ============================================
pause
