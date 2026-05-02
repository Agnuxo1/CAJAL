@echo off
cd /d D:\PROJECTS\CAJAL
echo ========================================
echo CAJAL-27B Training Started
echo ========================================
echo %date% %time%
python scripts/train_cajal.py --model qwen3.5-27b --local-model-path "D:\PROJECTS\CAJAL\Modelos originales\Qwen3.6-27B-HF" --dataset "D:\PROJECTS\CAJAL\cajal_dataset.jsonl" --output-name CAJAL-27B --output-dir "D:\PROJECTS\CAJAL\outputs" --max-seq-length 2048 --batch-size 1 --grad-accum 8 --epochs 1 --use-thinking --lr 2e-4 2>&1
echo ========================================
echo CAJAL-27B Training Finished
echo ========================================
echo %date% %time%
pause
