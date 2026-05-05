#!/bin/bash
# CAJAL-9B GGUF Conversion Script
# Optimized for scientific paper generation
# Part of P2PCLAW Ecosystem

set -e

MODEL_NAME="CAJAL-9B-P2PCLAW"
HF_MODEL="Agnuxo/CAJAL-9B-P2PCLAW"
BASE_MODEL="Qwen3.6-9B-Instruct"

echo "=== CAJAL-9B GGUF Conversion ==="
echo "Converting $MODEL_NAME to GGUF format..."

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Install llama.cpp conversion tools if needed
if [ ! -d "llama.cpp" ]; then
    echo "Cloning llama.cpp..."
    git clone --depth 1 https://github.com/ggml-org/llama.cpp.git
fi

# Install Python requirements
cd llama.cpp
pip install -r requirements/requirements-convert-hf-to-gguf.txt 2>/dev/null || true

# Download model from HuggingFace
echo "Downloading model from HuggingFace..."
if ! command -v huggingface-cli &> /dev/null; then
    pip install huggingface-hub
fi

huggingface-cli download $HF_MODEL --local-dir ./cajal-9b-hf --local-dir-use-symlinks False

# Convert to GGUF
echo "Converting to GGUF (Q4_K_M - 4.5GB)..."
python3 convert_hf_to_gguf.py \
    --src ./cajal-9b-hf \
    --dst ./cajal-9b-q4_k_m.gguf \
    --outtype q4_k_m

# Also create Q5_K_M (higher quality, ~5.5GB)
echo "Converting to GGUF (Q5_K_M - 5.5GB)..."
python3 convert_hf_to_gguf.py \
    --src ./cajal-9b-hf \
    --dst ./cajal-9b-q5_k_m.gguf \
    --outtype q5_k_m

# Create Ollama Modelfile
cat > Modelfile.CAJAL-9B << 'EOF'
FROM ./cajal-9b-q4_k_m.gguf
PARAMETER temperature 0.3
PARAMETER top_p 0.8
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 32768
SYSTEM "You are CAJAL-9B, a specialized AI for generating scientific papers..."
EOF

echo "=== Conversion Complete ==="
echo "Files created:"
echo "  - cajal-9b-q4_k_m.gguf (~4.5GB)"
echo "  - cajal-9b-q5_k_m.gguf (~5.5GB)"
echo "  - Modelfile.CAJAL-9B"
echo ""
echo "Test with:"
echo "  ollama create cajal-9b -f Modelfile.CAJAL-9B"
echo "  ollama run cajal-9b"
