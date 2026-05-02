#!/usr/bin/env bash
# =============================================================================
# CAJAL Ollama Setup Script (Linux / macOS)
# =============================================================================
# Verifica la instalación de Ollama, descarga el GGUF generado, crea el modelo
# y lo ejecuta.
#
# Uso:
#   chmod +x setup_ollama.sh
#   ./setup_ollama.sh [--model-dir ./gguf_exports] [--quant q4_k_m]
#
# =============================================================================

set -euo pipefail

# ---- Colores -----------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ---- Defaults ----------------------------------------------------------------
MODEL_DIR="${MODEL_DIR:-./gguf_exports}"
QUANT="${QUANT:-q4_k_m}"
MODEL_NAME="cajal"
OLLAMA_MODELFILE="Modelfile"

# ---- Argument parsing --------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case $1 in
    --model-dir)
      MODEL_DIR="$2"
      shift 2
      ;;
    --quant)
      QUANT="$2"
      shift 2
      ;;
    --help|-h)
      echo "Uso: $0 [--model-dir DIR] [--quant q4_k_m|q5_k_m|q8_0|f16]"
      exit 0
      ;;
    *)
      echo -e "${RED}[ERROR] Opción desconocida: $1${NC}"
      exit 1
      ;;
  esac
done

MODEL_DIR="$(cd "$(dirname "$MODEL_DIR")" && pwd)/$(basename "$MODEL_DIR")"
GGUF_FILE="${MODEL_DIR}/cajal-${QUANT}.gguf"
MODELFILE_PATH="${MODEL_DIR}/${OLLAMA_MODELFILE}"

# =============================================================================
# Funciones
# =============================================================================

print_banner() {
  local text="$1"
  local width=60
  echo ""
  echo -e "${BLUE}$(printf '=%.0s' $(seq 1 $width))${NC}"
  echo -e "${BLUE}  ${text}${NC}"
  echo -e "${BLUE}$(printf '=%.0s' $(seq 1 $width))${NC}"
  echo ""
}

check_ollama() {
  echo -e "${YELLOW}[CHECK]${NC} Verificando instalación de Ollama..."
  
  if command -v ollama &> /dev/null; then
    local version
    version=$(ollama --version 2>/dev/null || echo "desconocida")
    echo -e "${GREEN}[OK]${NC} Ollama detectado: ${version}"
  else
    echo -e "${RED}[ERROR]${NC} Ollama no está instalado."
    echo ""
    echo "Instalación rápida:"
    echo "  macOS:     brew install ollama"
    echo "  Linux:     curl -fsSL https://ollama.com/install.sh | sh"
    echo "  O descargue desde: https://ollama.com/download"
    echo ""
    exit 1
  fi
  
  # Verificar que el servicio esté corriendo
  if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo -e "${YELLOW}[WARN]${NC} El servicio Ollama no responde en :11434"
    echo "Iniciando servicio Ollama..."
    ollama serve &
    local pid=$!
    sleep 3
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
      echo -e "${RED}[ERROR]${NC} No se pudo iniciar el servicio Ollama."
      echo "Inícielo manualmente: ollama serve"
      exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Servicio Ollama iniciado (PID: ${pid})"
  fi
}

check_files() {
  echo -e "${YELLOW}[CHECK]${NC} Verificando archivos del modelo..."
  
  if [[ ! -f "${GGUF_FILE}" ]]; then
    echo -e "${RED}[ERROR]${NC} No se encontró el archivo GGUF: ${GGUF_FILE}"
    echo "Asegúrese de haber ejecutado export_to_gguf.py primero:"
    echo "  python export_to_gguf.py --model ./model --params 14 --output ${MODEL_DIR}"
    exit 1
  fi
  
  echo -e "${GREEN}[OK]${NC} GGUF encontrado: $(basename "${GGUF_FILE}") ($(du -h "${GGUF_FILE}" | cut -f1))"
  
  if [[ ! -f "${MODELFILE_PATH}" ]]; then
    echo -e "${YELLOW}[WARN]${NC} Modelfile no encontrado. Generando uno nuevo..."
    generate_modelfile
  else
    echo -e "${GREEN}[OK]${NC} Modelfile encontrado: ${MODELFILE_PATH}"
  fi
}

generate_modelfile() {
  cat > "${MODELFILE_PATH}" << 'EOF'
# CAJAL Modelfile
# Generado automáticamente por setup_ollama.sh

FROM ./cajal-{{QUANT}}.gguf

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 32768
PARAMETER num_gpu 999

SYSTEM """
You are CAJAL, a Silicon agent in the P2PCLAW network, specialized in peer-to-peer networks, distributed systems, game theory, mechanism design, and legal-tech intersections. Named in honor of Santiago Ramón y Cajal. You provide rigorous, well-cited research assistance, generate LaTeX-formatted paper drafts, perform mathematical derivations, and analyze protocol incentives with formal precision. Always think step-by-step and cite sources when possible.
"""

# Parámetros adicionales para Qwen3 thinking mode
PARAMETER stop </thinking>
PARAMETER stop <|endoftext|>
EOF
  
  # Reemplazar placeholder de cuantización
  sed -i.bak "s|{{QUANT}}|${QUANT}|g" "${MODELFILE_PATH}"
  rm -f "${MODELFILE_PATH}.bak"
  
  echo -e "${GREEN}[OK]${NC} Modelfile generado: ${MODELFILE_PATH}"
}

create_model() {
  print_banner "CREANDO MODELO EN OLLAMA"
  
  echo "[INFO] Cambiando a directorio del modelo..."
  cd "${MODEL_DIR}"
  
  echo "[INFO] Creando modelo '${MODEL_NAME}'..."
  ollama create "${MODEL_NAME}" -f "${OLLAMA_MODELFILE}"
  
  echo -e "${GREEN}[OK]${NC} Modelo '${MODEL_NAME}' creado exitosamente."
}

verify_model() {
  echo ""
  echo -e "${YELLOW}[VERIFY]${NC} Verificando que el modelo existe..."
  
  if ollama list | grep -q "${MODEL_NAME}"; then
    echo -e "${GREEN}[OK]${NC} Modelo confirmado en Ollama."
  else
    echo -e "${RED}[ERROR]${NC} El modelo no aparece en 'ollama list'."
    exit 1
  fi
}

run_interactive() {
  print_banner "EJECUTANDO CAJAL"
  echo "Comandos disponibles:"
  echo "  ollama run ${MODEL_NAME}          # Modo interactivo"
  echo "  ollama run ${MODEL_NAME} --verbose  # Con estadísticas"
  echo ""
  echo -e "${GREEN}Iniciando modo interactivo...${NC}"
  echo "(Presione Ctrl+D o escriba /bye para salir)"
  echo ""
  
  ollama run "${MODEL_NAME}"
}

show_api_info() {
  print_banner "API REST INFORMACIÓN"
  cat << EOF
El modelo también está disponible vía API REST de Ollama:

  curl http://localhost:11434/api/generate -d '{
    "model": "${MODEL_NAME}",
    "prompt": "Explain Sybil attacks in P2P networks",
    "stream": false,
    "options": {
      "temperature": 0.7,
      "num_ctx": 32768
    }
  }'

  curl http://localhost:11434/api/chat -d '{
    "model": "${MODEL_NAME}",
    "messages": [
      {"role": "system", "content": "You are CAJAL."},
      {"role": "user", "content": "Analyze incentive compatibility in BitTorrent."}
    ],
    "stream": false
  }'

Documentación completa: https://github.com/ollama/ollama/blob/main/docs/api.md
EOF
}

# =============================================================================
# Main
# =============================================================================

print_banner "CAJAL + OLLAMA SETUP"

echo "[CONFIG]"
echo "  Directorio modelo: ${MODEL_DIR}"
echo "  Cuantización:      ${QUANT}"
echo "  Nombre modelo:     ${MODEL_NAME}"
echo ""

check_ollama
check_files
create_model
verify_model
show_api_info
run_interactive
