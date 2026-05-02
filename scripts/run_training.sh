#!/bin/bash
# CAJAL Training Script - Runs inside WSL2 or Docker
# Usage: bash run_training.sh [model_size]
# model_size: 27b (default), 9b, 4b

set -e

MODEL_SIZE=${1:-27b}
WORKSPACE="/workspace"

case "$MODEL_SIZE" in
    27b)
        MODEL_NAME="qwen3.6-27b"
        OUTPUT_NAME="CAJAL-27B"
        LOCAL_MODEL="/workspace/models/Qwen3.6-27B-HF"
        ;;
    9b)
        MODEL_NAME="qwen3.5-9b"
        OUTPUT_NAME="CAJAL-9B"
        LOCAL_MODEL=""
        ;;
    4b)
        MODEL_NAME="qwen3.5-4b"
        OUTPUT_NAME="CAJAL-4B"
        LOCAL_MODEL=""
        ;;
    *)
        echo "Unknown model size: $MODEL_SIZE"
        echo "Usage: bash run_training.sh [27b|9b|4b]"
        exit 1
        ;;
esac

echo "========================================"
echo "CAJAL Training - $OUTPUT_NAME"
echo "========================================"
echo "Model: $MODEL_NAME"
echo "Time: $(date)"
echo ""

DATASET="$WORKSPACE/cajal_dataset.jsonl"
OUTPUT_DIR="$WORKSPACE/outputs"

if [ -f "$DATASET" ]; then
    LOCAL_DATA_ARG="--dataset $DATASET"
else
    echo "WARNING: Dataset not found at $DATASET"
    echo "Looking for alternative locations..."
    for f in "$WORKSPACE/datasets/p2pclaw_train_hq_qwen3.jsonl" "$WORKSPACE/datasets/cajal_dataset.jsonl"; do
        if [ -f "$f" ]; then
            DATASET="$f"
            LOCAL_DATA_ARG="--dataset $DATASET"
            echo "Found dataset at $f"
            break
        fi
    done
fi

LOCAL_MODEL_ARG=""
if [ -n "$LOCAL_MODEL" ] && [ -d "$LOCAL_MODEL" ]; then
    LOCAL_MODEL_ARG="--local-model-path $LOCAL_MODEL"
    echo "Using local model: $LOCAL_MODEL"
else
    echo "Will download model from HuggingFace"
fi

python "$WORKSPACE/scripts/train_cajal_unsloth.py" \
    --model "$MODEL_NAME" \
    $LOCAL_MODEL_ARG \
    $LOCAL_DATA_ARG \
    --output-dir "$OUTPUT_DIR" \
    --output-name "$OUTPUT_NAME" \
    --epochs 1 \
    --batch-size 1 \
    --grad-accum 8 \
    --lr 2e-4 \
    --max-seq-length 2048 \
    --lora-r 16 \
    --lora-alpha 16 \
    --use-thinking \
    --save-merged \
    --export-gguf \
    --gguf-quant q4_k_m \
    2>&1 | tee "$WORKSPACE/training_${OUTPUT_NAME}.log"

echo "========================================"
echo "CAJAL $OUTPUT_NAME Training Finished"
echo "========================================"
echo "$(date)"