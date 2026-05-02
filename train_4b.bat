@echo off
cd /d D:\PROJECTS\CAJAL
echo ========================================
echo CAJAL-4B Training Started
echo ========================================
echo %date% %time%

python scripts\train_cajal_4b.py ^
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
    --export-gguf ^
    --gguf-quant q4_k_m

echo ========================================
echo CAJAL-4B Training Finished
echo ========================================
echo %date% %time%
pause