#!/usr/bin/env bash
# CAJAL One-Click Installer for Linux / macOS
# Usage: curl -fsSL https://p2pclaw.com/silicon/install.sh | bash

set -e

VERSION="1.0.0"
INSTALL_DIR="${HOME}/cajal"
MODEL_PATH=""
SKIP_MODEL=0
NO_OLLAMA_CHECK=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

header() {
    echo -e "${CYAN}\n========================================"
    echo -e "  $1"
    echo -e "========================================${NC}"
}

step() {
    echo -e "${GREEN}[+] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[!] $1${NC}"
}

err() {
    echo -e "${RED}[X] $1${NC}"
}

header "CAJAL Ecosystem Installer v${VERSION}"
echo "P2PCLAW Lab, Zurich | https://p2pclaw.com/silicon"
echo ""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-dir) INSTALL_DIR="$2"; shift 2 ;;
        --model-path) MODEL_PATH="$2"; shift 2 ;;
        --skip-model) SKIP_MODEL=1; shift ;;
        --no-ollama-check) NO_OLLAMA_CHECK=1; shift ;;
        *) shift ;;
    esac
done

# Detect OS
OS="linux"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
fi

step "Detected OS: $OS"

# Check prerequisites
step "Checking prerequisites..."

# Check for curl or wget
if command -v curl &>/dev/null; then
    FETCH="curl -fsSL"
elif command -v wget &>/dev/null; then
    FETCH="wget -qO-"
else
    err "curl or wget is required."
    exit 1
fi

# Check Python
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    err "Python 3 is required. Install it with your package manager."
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1)
step "Python found: $PY_VERSION"

# Check / Install Ollama
if [[ $NO_OLLAMA_CHECK -eq 0 ]]; then
    if ! command -v ollama &>/dev/null; then
        warn "Ollama not found."
        read -p "Install Ollama now? [Y/n] " resp
        if [[ -z "$resp" || "$resp" =~ ^[Yy]$ ]]; then
            step "Installing Ollama..."
            curl -fsSL https://ollama.com/install.sh | sh
            step "Ollama installed."
        else
            warn "Skipping Ollama. CAJAL requires it to run."
        fi
    else
        step "Ollama found: $(which ollama)"
    fi
fi

# Create directories
step "Creating CAJAL directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"/{models,cli,webapp,integrations}

# Download ecosystem files
step "Downloading CAJAL ecosystem..."
BASE_URL="https://raw.githubusercontent.com/p2pclaw/cajal/main/ecosystem"

for file in cli/cajal.py cli/requirements.txt webapp/index.html webapp/app.js webapp/styles.css; do
    mkdir -p "$(dirname "$INSTALL_DIR/$file")"
    if $FETCH "$BASE_URL/$file" > "$INSTALL_DIR/$file" 2>/dev/null; then
        true
    else
        warn "Could not download $file"
    fi
done

# Install Python deps
step "Installing Python dependencies..."
$PYTHON -m pip install --user -q -r "$INSTALL_DIR/cli/requirements.txt" 2>/dev/null || true

# Setup model
MODEL_DIR="$INSTALL_DIR/models"
MODELFILE="$MODEL_DIR/Modelfile"

if [[ -n "$MODEL_PATH" && -f "$MODEL_PATH" ]]; then
    step "Using provided model: $MODEL_PATH"
    cp "$MODEL_PATH" "$MODEL_DIR/"
    MODEL_DIR=$(dirname "$MODEL_PATH")
else
    if [[ -f "$MODEL_DIR/CAJAL-4B-f16.gguf" ]]; then
        step "Found local model."
    else
        warn "CAJAL-4B model not found locally."
        if [[ $SKIP_MODEL -eq 0 ]]; then
            read -p "Download CAJAL-4B (~8.4 GB)? [y/N] " dl
            if [[ "$dl" =~ ^[Yy]$ ]]; then
                step "Downloading CAJAL-4B (this will take time)..."
                MODEL_URL="https://huggingface.co/p2pclaw/cajal-4b/resolve/main/CAJAL-4B-f16.gguf"
                if command -v curl &>/dev/null; then
                    curl -L -o "$MODEL_DIR/CAJAL-4B-f16.gguf" "$MODEL_URL" || warn "Download failed"
                else
                    wget -O "$MODEL_DIR/CAJAL-4B-f16.gguf" "$MODEL_URL" || warn "Download failed"
                fi
            else
                warn "Skipping model download."
            fi
        fi
    fi
fi

# Create Modelfile
if ls "$MODEL_DIR"/*.gguf 1>/dev/null 2>&1; then
    GGUF=$(ls "$MODEL_DIR"/*.gguf | head -1)
    REL=$(basename "$GGUF")
    cat > "$MODELFILE" << 'EOF'
FROM ./CAJAL-4B-f16.gguf

TEMPLATE """{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ range .Messages }}{{ if eq .Role "user" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{ else if eq .Role "assistant" }}<|im_start|>assistant
{{ .Content }}<|im_end|>
{{ end }}{{ end }}<|im_start|>assistant
<think>
"""

SYSTEM """You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland..."""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER stop <|im_end|>
EOF
    cp "$MODELFILE" "$MODEL_DIR/Modelfile"
fi

# Install into Ollama
if [[ $SKIP_MODEL -eq 0 && -f "$MODEL_DIR/Modelfile" && -f "$MODEL_DIR/CAJAL-4B-f16.gguf" ]]; then
    step "Installing CAJAL-4B into Ollama..."
    (
        cd "$MODEL_DIR"
        ollama create cajal-4b -f Modelfile 2>&1 | grep -E "(success|error)" || true
    )
    step "CAJAL-4B registered in Ollama!"
fi

# Create launcher scripts
cat > "$INSTALL_DIR/cajal-cli" << 'EOF'
#!/usr/bin/env bash
python3 "$HOME/cajal/cli/cajal.py" "$@"
EOF
chmod +x "$INSTALL_DIR/cajal-cli"

cat > "$INSTALL_DIR/start-webapp" << 'EOF'
#!/usr/bin/env bash
echo "Opening CAJAL Web Chat..."
if command -v xdg-open &>/dev/null; then
    xdg-open "$HOME/cajal/webapp/index.html"
elif command -v open &>/dev/null; then
    open "$HOME/cajal/webapp/index.html"
else
    echo "Open this file in your browser: $HOME/cajal/webapp/index.html"
fi
EOF
chmod +x "$INSTALL_DIR/start-webapp"

# Add to PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    step "Adding CAJAL to PATH..."
    SHELL_RC=""
    if [[ "$SHELL" == */zsh ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ "$SHELL" == */bash ]]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    if [[ -n "$SHELL_RC" ]]; then
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_RC"
        echo "alias cajal='cajal-cli chat'" >> "$SHELL_RC"
    fi
fi

# Final summary
header "Installation Complete!"
echo ""
echo -e "${GREEN}CAJAL-4B is installed at: $INSTALL_DIR${NC}"
echo ""
echo -e "${CYAN}Quick Start Commands:${NC}"
echo "  cajal-cli status      Check system status"
echo "  cajal-cli chat        Interactive chat"
echo "  cajal-cli ask Q       Ask a question"
echo "  cajal-cli serve       Start API server"
echo "  cajal-cli config      Edit settings"
echo ""
echo "Web Chat:     $INSTALL_DIR/start-webapp"
echo "API Endpoint: http://localhost:8765/v1/chat/completions"
echo ""
echo -e "${MAGENTA}Connect to P2PCLAW: https://p2pclaw.com/silicon${NC}"
echo ""

read -p "Start CAJAL chat now? [Y/n] " start
if [[ -z "$start" || "$start" =~ ^[Yy]$ ]]; then
    echo "Starting CAJAL chat..."
    $PYTHON "$INSTALL_DIR/cli/cajal.py" chat
fi
