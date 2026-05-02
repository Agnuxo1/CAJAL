#!/usr/bin/env bash
# CAJAL-4B Integration Ecosystem - Build Script
# Builds all packages and integrations

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/dist"

echo "============================================"
echo "  CAJAL-4B Integration Ecosystem Build"
echo "  P2PCLAW Lab, Zurich"
echo "============================================"

mkdir -p "$OUTPUT_DIR"

# [1] Build PyPI package
echo ""
echo "[1/5] Building PyPI package (cajal-cli)..."
cd "$SCRIPT_DIR/pypi-package"
python3 -m pip install build twine --quiet 2>/dev/null || true
python3 -m build --outdir "$OUTPUT_DIR/pypi" 2>/dev/null || echo "  (build manually with: cd pypi-package && python3 -m build)"

# [2] Package LangChain integration
echo ""
echo "[2/5] Packaging LangChain integration..."
cd "$SCRIPT_DIR/integrations/langchain"
mkdir -p "$OUTPUT_DIR/langchain"
cp -r *.py setup.py "$OUTPUT_DIR/langchain/" 2>/dev/null || true
cat > "$OUTPUT_DIR/langchain/README.md" << 'EOF'
# cajal-langchain

LangChain integration for CAJAL-4B.

```bash
pip install cajal-langchain
```

```python
from cajal_langchain import CajalLLM
llm = CajalLLM()
result = llm.invoke("Explain P2PCLAW")
```
EOF

# [3] Package LlamaIndex integration
echo ""
echo "[3/5] Packaging LlamaIndex integration..."
cd "$SCRIPT_DIR/integrations/llamaindex"
mkdir -p "$OUTPUT_DIR/llamaindex"
cp -r *.py "$OUTPUT_DIR/llamaindex/" 2>/dev/null || true
cat > "$OUTPUT_DIR/llamaindex/README.md" << 'EOF'
# cajal-llamaindex

LlamaIndex integration for CAJAL-4B.

```bash
pip install cajal-llamaindex
```

```python
from cajal_llama import CajalLlamaLLM
from llama_index.core import Settings
Settings.llm = CajalLlamaLLM()
```
EOF

# [4] Package CrewAI integration
echo ""
echo "[4/5] Packaging CrewAI integration..."
cd "$SCRIPT_DIR/integrations/crewai"
mkdir -p "$OUTPUT_DIR/crewai"
cp -r *.py "$OUTPUT_DIR/crewai/" 2>/dev/null || true
cat > "$OUTPUT_DIR/crewai/README.md" << 'EOF'
# cajal-crewai

CrewAI tools for CAJAL-4B.

```bash
pip install cajal-crewai
```

```python
from cajal_crewai import CajalTool
tool = CajalTool()
result = tool.run("Research P2PCLAW governance")
```
EOF

# [5] Package scripts and configs
echo ""
echo "[5/5] Packaging scripts and configurations..."
mkdir -p "$OUTPUT_DIR/scripts"
cp "$SCRIPT_DIR/scripts/cajal-setup.py" "$OUTPUT_DIR/scripts/"
cp "$SCRIPT_DIR/scripts/publish-pypi.sh" "$OUTPUT_DIR/scripts/"

mkdir -p "$OUTPUT_DIR/pinokio"
cp "$SCRIPT_DIR/pinokio/launcher.json" "$OUTPUT_DIR/pinokio/"

mkdir -p "$OUTPUT_DIR/open-webui"
cp "$SCRIPT_DIR/open-webui/cajal_tool.py" "$OUTPUT_DIR/open-webui/"

# Summary
echo ""
echo "============================================"
echo "  Build Complete!"
echo "  Output: $OUTPUT_DIR"
echo "============================================"
echo ""
find "$OUTPUT_DIR" -type f | head -30
echo ""
echo "Packages built:"
echo "  - PyPI: $OUTPUT_DIR/pypi/"
echo "  - LangChain: $OUTPUT_DIR/langchain/"
echo "  - LlamaIndex: $OUTPUT_DIR/llamaindex/"
echo "  - CrewAI: $OUTPUT_DIR/crewai/"
echo "  - Scripts: $OUTPUT_DIR/scripts/"
echo "  - Pinokio: $OUTPUT_DIR/pinokio/"
echo "  - Open WebUI: $OUTPUT_DIR/open-webui/"
