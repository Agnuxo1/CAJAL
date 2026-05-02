#!/usr/bin/env bash
# ============================================================
# CAJAL Training Launcher (Linux / macOS)
# ============================================================

set -euo pipefail

# Default paths
DATASET="${DATASET:-./datasets/p2pclaw_train_hq.jsonl}"
OUTPUT_NAME="${OUTPUT_NAME:-CAJAL}"
OUTPUT_DIR="${OUTPUT_DIR:-./outputs}"

# Detect OS for vram monitoring
MONITOR_VRAM=false
if command -v nvidia-smi &> /dev/null; then
    MONITOR_VRAM=true
fi

show_help() {
    cat << 'EOF'
Usage: ./train.sh [MODEL_TYPE]

MODEL_TYPE options:
  qwen3-4b      (RECOMMENDED) ~6-8GB VRAM, fast, Apache 2.0
  qwen3-8b      ~10-12GB VRAM, more capable
  gemma4-e4b    ~6-10GB VRAM, 256K context, multimodal
  gemma4-26b    ~14-16GB VRAM, MoE, largest capacity
  help          Show this help message

Environment variables:
  DATASET       Path to JSONL dataset (default: ./datasets/p2pclaw_train_hq.jsonl)
  OUTPUT_NAME   Model name prefix (default: CAJAL)
  OUTPUT_DIR    Output directory (default: ./outputs)
  EPOCHS        Training epochs (default: 3)
  LR            Learning rate (default: 2e-4)
  LORA_R        LoRA rank (default: 32)
  MAX_LEN       Max sequence length (default: 8192)

Examples:
  ./train.sh qwen3-4b
  DATASET=./my_papers.jsonl EPOCHS=5 ./train.sh qwen3-8b
EOF
}

MODEL="${1:-qwen3-4b}"

if [ "$MODEL" == "help" ] || [ "$MODEL" == "--help" ] || [ "$MODEL" == "-h" ]; then
    show_help
    exit 0
fi

case "$MODEL" in
    qwen3-4b|qwen3-8b|gemma4-e4b|gemma4-26b)
        ;;
    *)
        echo "ERROR: Unknown model '$MODEL'"
        show_help
        exit 1
        ;;
esac

EPOCHS="${EPOCHS:-3}"
LR="${LR:-2e-4}"
LORA_R="${LORA_R:-32}"
MAX_LEN="${MAX_LEN:-8192}"

echo "=============================================="
echo "  CAJAL Training"
echo "=============================================="
echo "  Model:       $MODEL"
echo "  Dataset:     $DATASET"
echo "  Output:      $OUTPUT_NAME"
echo "  Epochs:      $EPOCHS"
echo "  LR:          $LR"
echo "  LoRA r:      $LORA_R"
echo "  Max length:  $MAX_LEN"
echo "=============================================="

if [ "$MONITOR_VRAM" = true ]; then
    echo ""
    echo "Initial GPU status:"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
    echo ""
fi

# Build command
CMD=(
    python train_cajal.py
    --model "$MODEL"
    --dataset "$DATASET"
    --output-name "$OUTPUT_NAME"
    --output-dir "$OUTPUT_DIR"
    --epochs "$EPOCHS"
    --lr "$LR"
    --lora-r "$LORA_R"
    --max-seq-length "$MAX_LEN"
    --export-gguf
    --save-merged
)

# Model-specific recommendations
if [ "$MODEL" == "qwen3-4b" ]; then
    echo "Using recommended settings for Qwen3-4B (conservative, fast)"
    CMD+=(
        --batch-size 2
        --grad-accum 4
        --lora-alpha 64
        --use-thinking
    )
elif [ "$MODEL" == "qwen3-8b" ]; then
    echo "Using recommended settings for Qwen3-8B (moderate)"
    CMD+=(
        --batch-size 1
        --grad-accum 8
        --lora-alpha 64
        --use-thinking
    )
elif [ "$MODEL" == "gemma4-e4b" ]; then
    echo "Using recommended settings for Gemma 4 E4B"
    CMD+=(
        --batch-size 2
        --grad-accum 4
        --lora-alpha 64
    )
elif [ "$MODEL" == "gemma4-26b" ]; then
    echo "Using recommended settings for Gemma 4 26B (tight VRAM)"
    CMD+=(
        --batch-size 1
        --grad-accum 8
        --lora-alpha 32
        --lora-r 16
        --max-seq-length 4096
    )
fi

echo ""
echo "Running command:"
echo "${CMD[*]}"
echo ""

# Execute training
"${CMD[@]}"

EXIT_CODE=$?

if [ "$MONITOR_VRAM" = true ]; then
    echo ""
    echo "Final GPU status:"
    nvidia-smi --query-gpu=name,memory.used,memory.free --format=csv,noheader
fi

echo ""
echo "=============================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "  Training completed successfully!"
    echo "  Outputs in: $OUTPUT_DIR"
else
    echo "  Training failed with exit code $EXIT_CODE"
fi
echo "=============================================="

exit $EXIT_CODE
