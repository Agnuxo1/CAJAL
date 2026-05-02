@echo off
REM ============================================================
REM CAJAL Training Launcher (Windows)
REM ============================================================
setlocal EnableDelayedExpansion

REM Default paths
if "!DATASET!"=="" set "DATASET=./datasets/p2pclaw_train_hq.jsonl"
if "!OUTPUT_NAME!"=="" set "OUTPUT_NAME=CAJAL"
if "!OUTPUT_DIR!"=="" set "OUTPUT_DIR=./outputs"

REM Parse arguments
set "MODEL=%1"
if "!MODEL!"=="" set "MODEL=qwen3-4b"

if "!MODEL!"=="help" goto :show_help
if "!MODEL!"=="--help" goto :show_help
if "!MODEL!"=="-h" goto :show_help

if "!MODEL!"=="qwen3-4b" goto :valid
if "!MODEL!"=="qwen3-8b" goto :valid
if "!MODEL!"=="gemma4-e4b" goto :valid
if "!MODEL!"=="gemma4-26b" goto :valid

echo ERROR: Unknown model '!MODEL!'
goto :show_help

:valid
REM Set defaults
if "!EPOCHS!"=="" set "EPOCHS=3"
if "!LR!"=="" set "LR=2e-4"
if "!LORA_R!"=="" set "LORA_R=32"
if "!MAX_LEN!"=="" set "MAX_LEN=8192"

echo ==============================================
echo   CAJAL Training
echo ==============================================
echo   Model:       !MODEL!
echo   Dataset:     !DATASET!
echo   Output:      !OUTPUT_NAME!
echo   Epochs:      !EPOCHS!
echo   LR:          !LR!
echo   LoRA r:      !LORA_R!
echo   Max length:  !MAX_LEN!
echo ==============================================

REM Build base command
set "CMD=python train_cajal.py --model !MODEL! --dataset !DATASET! --output-name !OUTPUT_NAME! --output-dir !OUTPUT_DIR! --epochs !EPOCHS! --lr !LR! --lora-r !LORA_R! --max-seq-length !MAX_LEN! --export-gguf --save-merged"

REM Model-specific recommendations
if "!MODEL!"=="qwen3-4b" (
    echo Using recommended settings for Qwen3-4B (conservative, fast)
    set "CMD=!CMD! --batch-size 2 --grad-accum 4 --lora-alpha 64 --use-thinking"
) else if "!MODEL!"=="qwen3-8b" (
    echo Using recommended settings for Qwen3-8B (moderate)
    set "CMD=!CMD! --batch-size 1 --grad-accum 8 --lora-alpha 64 --use-thinking"
) else if "!MODEL!"=="gemma4-e4b" (
    echo Using recommended settings for Gemma 4 E4B
    set "CMD=!CMD! --batch-size 2 --grad-accum 4 --lora-alpha 64"
) else if "!MODEL!"=="gemma4-26b" (
    echo Using recommended settings for Gemma 4 26B (tight VRAM)
    set "CMD=!CMD! --batch-size 1 --grad-accum 8 --lora-alpha 32 --lora-r 16 --max-seq-length 4096"
)

echo.
echo Running command:
echo !CMD!
echo.

REM Execute
!CMD!
set "EXIT_CODE=!ERRORLEVEL!"

echo.
echo ==============================================
if !EXIT_CODE! == 0 (
    echo   Training completed successfully!
    echo   Outputs in: !OUTPUT_DIR!
) else (
    echo   Training failed with exit code !EXIT_CODE!
)
echo ==============================================

exit /b !EXIT_CODE!

:show_help
echo Usage: train.bat [MODEL_TYPE]
echo.
echo MODEL_TYPE options:
echo   qwen3-4b      (RECOMMENDED) ~6-8GB VRAM, fast, Apache 2.0
echo   qwen3-8b      ~10-12GB VRAM, more capable
echo   gemma4-e4b    ~6-10GB VRAM, 256K context, multimodal
echo   gemma4-26b    ~14-16GB VRAM, MoE, largest capacity
echo   help          Show this help message
echo.
echo Environment variables:
echo   DATASET       Path to JSONL dataset
echo   OUTPUT_NAME   Model name prefix
echo   OUTPUT_DIR    Output directory
echo   EPOCHS        Training epochs
echo   LR            Learning rate
echo   LORA_R        LoRA rank
echo   MAX_LEN       Max sequence length
echo.
echo Examples:
echo   train.bat qwen3-4b
echo   set DATASET=./my_papers.jsonl^&^& set EPOCHS=5^&^& train.bat qwen3-8b
exit /b 0
