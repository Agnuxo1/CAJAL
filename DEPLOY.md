# CAJAL Deployment Guide

Guía completa para exportar, desplegar y ejecutar **CAJAL** en múltiples plataformas y configuraciones.

---

## Tabla de Contenidos

1. [Requisitos de Hardware](#1-requisitos-de-hardware)
2. [Instalación de Dependencias](#2-instalación-de-dependencias)
3. [Exportación del Modelo](#3-exportación-del-modelo)
4. [Opción A: Ollama Local](#opción-a-ollama-local)
5. [Opción B: API Server con FastAPI](#opción-b-api-server-con-fastapi)
6. [Opción C: Docker](#opción-c-docker)
7. [Opción D: Hugging Face Inference API](#opción-d-hugging-face-inference-api)
8. [Benchmarking de Velocidad](#8-benchmarking-de-velocidad)
9. [Troubleshooting Común](#9-troubleshooting-común)

---

## 1. Requisitos de Hardware

### Mínimos (Ejecución básica)

| Componente | Requisito |
|------------|-----------|
| GPU        | NVIDIA GTX 1080 Ti (11GB VRAM) o superior |
| RAM        | 32 GB DDR4 |
| Almacenamiento | 100 GB SSD |
| CPU        | 8 cores / 16 threads |
| Red        | Conexión estable para descargar modelos |

### Recomendados (Entrenamiento + Inferencia)

| Componente | Requisito |
|------------|-----------|
| GPU        | NVIDIA RTX 3090 (24GB VRAM) o RTX 4090 (24GB VRAM) |
| RAM        | 64 GB DDR4/DDR5 |
| Almacenamiento | 500 GB NVMe SSD |
| CPU        | 12+ cores moderno (Ryzen 5900X / Intel i7-12700K+) |
| OS         | Ubuntu 22.04 LTS (recomendado) o Windows 11 |

### Múltiples GPUs (Escalado)

Para modelos > 14B parámetros o inferencia concurrente:
- 2x RTX 3090 / 4090 con NVLink (opcional)
- vLLM tensor parallelism `--tensor-parallel 2`

---

## 2. Instalación de Dependencias

### Base (todas las plataformas)

```bash
# Python 3.10+
python -m pip install --upgrade pip

# Core dependencies
pip install torch>=2.4.0 transformers>=4.45.0 accelerate>=0.34.0
pip install fastapi uvicorn pydantic
pip install huggingface_hub

# Para exportación GGUF
pip install llama-cpp-python

# Para vLLM (Linux recomendado, CUDA 12.1+)
pip install vllm>=0.6.0

# Para entrenamiento (Unsloth)
pip install unsloth
```

### CUDA / NVIDIA Drivers

```bash
# Verificar instalación
nvidia-smi

# Debería mostzar:
# +---------------------------------------------------------------------------------------+
# | NVIDIA-SMI 535.104.05              Driver Version: 535.104.05   CUDA Version: 12.2    |
# +---------------------------------------------------------------------------------------+

# Si no tiene CUDA, instale:
# Ubuntu:
sudo apt update && sudo apt install -y nvidia-driver-535 nvidia-utils-535
sudo reboot

# Y CUDA toolkit:
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-1
```

### Docker + NVIDIA Container Toolkit

```bash
# Instalar Docker
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker

# NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

---

## 3. Exportación del Modelo

### Tabla Comparativa de Formatos de Exportación

| Formato | Método | Bits | Tamaño (7B) | Tamaño (14B) | Calidad | Uso Recomendado |
|---------|--------|------|-------------|--------------|---------|-----------------|
| **Q4_K_M** | K-quants | 4 | ~2.0 GB | ~4.0 GB | ★★★☆☆ Alta | **Uso general, chat, RAG** |
| **Q5_K_M** | K-quants | 5 | ~2.4 GB | ~4.8 GB | ★★★★☆ Muy alta | Reasoning, papers, análisis |
| **Q8_0** | Lineal | 8 | ~3.8 GB | ~7.5 GB | ★★★★★ Casi lossless | Máxima calidad, producción |
| **F16** | Flotante | 16 | ~7.0 GB | ~14.0 GB | ★★★★★ Perfecto | Referencia, fine-tuning base |
| **AWQ** | Activation-aware | 4 | ~2.0 GB | ~4.0 GB | ★★★☆☆ Alta | Inferencia GPU-only |
| **GPTQ** | Post-training | 4 | ~2.0 GB | ~4.0 GB | ★★★☆☆ Alta | Inferencia GPU-only |

> **Recomendación**: Para CAJAL en RTX 3090, use **Q4_K_M** para balance calidad/velocidad, o **Q5_K_M** si el contexto es principalmente research con razonamiento profundo.

### Exportar con el script

```bash
# Exportar modelo ya fusionado a todas las cuantizaciones
python scripts/export_to_gguf.py \
  --model ./merged_model \
  --params 14 \
  --output ./gguf_exports

# Exportar con LoRA (auto-merge)
python scripts/export_to_gguf.py \
  --model unsloth/Qwen2.5-14B-Instruct \
  --lora ./lora_adapter \
  --params 14 \
  --output ./gguf_exports

# Solo cuantizaciones específicas
python scripts/export_to_gguf.py \
  --model ./merged_model \
  --params 7 \
  --quants q4_k_m q5_k_m \
  --output ./gguf_exports

# Subir a HuggingFace (opcional)
python scripts/export_to_gguf.py \
  --model ./merged_model \
  --params 14 \
  --output ./gguf_exports \
  --push-to-hf tuusuario/cajal \
  --hf-token $HF_TOKEN
```

### Salida del script

El script genera:

```
./gguf_exports/
├── cajal-q4_k_m.gguf   # Recomendado
├── cajal-q5_k_m.gguf   # Alta calidad
├── cajal-q8_0.gguf     # Casi sin pérdida
├── cajal-f16.gguf      # Sin cuantizar
├── Modelfile                      # Para Ollama
└── lmstudio_config.json           # Para LM Studio
```

---

## Opción A: Ollama Local

### A.1 Requisitos

- [Ollama](https://ollama.com) instalado
- Script `setup_ollama.sh` (Linux/Mac) o `setup_ollama.ps1` (Windows)

### A.2 Linux / macOS

```bash
# 1. Dar permisos de ejecución
chmod +x scripts/setup_ollama.sh

# 2. Ejecutar (usa q4_k_m por defecto)
./scripts/setup_ollama.sh

# 3. Con cuantización específica
./scripts/setup_ollama.sh --model-dir ./gguf_exports --quant q5_k_m
```

### A.3 Windows (PowerShell)

```powershell
# 1. Permitir ejecución de scripts (si es necesario)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Ejecutar
.\scripts\setup_ollama.ps1

# 3. Con parámetros
.\scripts\setup_ollama.ps1 -ModelDir "C:\Models\p2pclaw" -Quant "q5_k_m"
```

### A.4 Uso manual (sin script)

```bash
# Verificar que Ollama está corriendo
curl http://localhost:11434/api/tags

# Crear modelo
cd ./gguf_exports
ollama create cajal -f Modelfile

# Ejecutar
ollama run cajal

# Ver modelos instalados
ollama list

# Eliminar modelo
ollama rm cajal
```

### A.5 API REST de Ollama

```bash
# Chat completions
curl http://localhost:11434/api/chat -d '{
  "model": "cajal",
  "messages": [
    {"role": "system", "content": "You are CAJAL."},
    {"role": "user", "content": "Explain Nash equilibrium in BitTorrent choking."}
  ],
  "stream": false,
  "options": {
    "temperature": 0.7,
    "num_ctx": 32768
  }
}'

# Generación simple
curl http://localhost:11434/api/generate -d '{
  "model": "cajal",
  "prompt": "Write a LaTeX abstract about Sybil-resistant P2P reputation systems.",
  "stream": false
}'

# Con streaming
curl http://localhost:11434/api/generate -d '{
  "model": "cajal",
  "prompt": "Analyze the legal implications of decentralized file sharing.",
  "stream": true
}'
```

---

## Opción B: API Server con FastAPI

### B.1 Requisitos

```bash
pip install fastapi uvicorn vllm
# o para GGUF:
pip install fastapi uvicorn llama-cpp-python
```

### B.2 Desplegar modelo HuggingFace / Fusionado

```bash
# Modelo ya fusionado (vLLM)
python scripts/deploy_local_server.py \
  --model ./merged_model \
  --type hf \
  --port 8000 \
  --context-length 32768

# Con LoRA sobre modelo base
python scripts/deploy_local_server.py \
  --model Qwen/Qwen2.5-14B-Instruct \
  --type lora \
  --lora ./lora_adapter \
  --port 8000
```

### B.3 Desplegar modelo GGUF

```bash
python scripts/deploy_local_server.py \
  --model ./gguf_exports/cajal-q4_k_m.gguf \
  --type gguf \
  --port 8000 \
  --context-length 32768
```

### B.4 Endpoints disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Healthcheck del servicio |
| GET | `/v1/models` | Listar modelos (OpenAI-compatible) |
| POST | `/v1/chat/completions` | Chat completions (OpenAI-compatible) |
| POST | `/v1/completions` | Text completions (OpenAI-compatible) |
| POST | `/generate_paper` | Generar borrador de paper académico |

### B.5 Ejemplos de uso

```bash
# Healthcheck
curl http://localhost:8000/health

# List models
curl http://localhost:8000/v1/models

# Chat completion (non-streaming)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cajal",
    "messages": [
      {"role": "system", "content": "You are CAJAL."},
      {"role": "user", "content": "Design a proof-of-reputation protocol."}
    ],
    "temperature": 0.7,
    "max_tokens": 4096
  }'

# Chat completion (streaming)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cajal",
    "messages": [{"role": "user", "content": "Explain game theory in P2P networks."}],
    "stream": true
  }'

# Thinking mode (Qwen3)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cajal",
    "messages": [{"role": "user", "content": "Prove that the protocol is incentive-compatible."}],
    "thinking_mode": true,
    "max_tokens": 8192
  }'

# Tool use
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cajal",
    "messages": [{"role": "user", "content": "Calculate the expected utility for a rational peer."}],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "calculate_utility",
          "description": "Calculate expected utility",
          "parameters": {"type": "object", "properties": {}}
        }
      }
    ]
  }'

# Generar paper (especializado P2PCLAW)
curl -X POST http://localhost:8000/generate_paper \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Decentralized reputation systems with formal game-theoretic guarantees",
    "style": "academic",
    "latex_format": true,
    "include_references": true,
    "max_tokens": 8192
  }'
```

### B.6 Configuración avanzada vLLM

```bash
# Múltiples GPUs
python scripts/deploy_local_server.py \
  --model ./merged_model \
  --type hf \
  --tensor-parallel 2 \
  --gpu-memory-utilization 0.95

# Limitar longitud de secuencia (para ahorrar VRAM)
python scripts/deploy_local_server.py \
  --model ./merged_model \
  --type hf \
  --max-model-len 16384 \
  --context-length 16384

# Chat template personalizado
python scripts/deploy_local_server.py \
  --model ./merged_model \
  --type hf \
  --chat-template ./custom_chat_template.jinja
```

---

## Opción C: Docker

### C.1 Requisitos

- Docker + Docker Compose
- NVIDIA Container Toolkit (para GPU)

### C.2 Preparar directorio de modelos

```bash
mkdir -p ./models
mkdir -p ./logs

# Copiar modelo GGUF o HF
cp ./gguf_exports/cajal-q4_k_m.gguf ./models/
# o
# cp -r ./merged_model ./models/
```

### C.3 Configurar variables de entorno

Cree un archivo `.env` en el mismo directorio que `docker-compose.yml`:

```env
# .env
MODELS_DIR=./models
LOGS_DIR=./logs
MODEL_PATH=/app/models/cajal-q4_k_m.gguf
MODEL_TYPE=gguf
BACKEND=llama-cpp
API_PORT=8000
CONTEXT_LENGTH=32768
GPU_MEMORY_UTILIZATION=0.90
TENSOR_PARALLEL_SIZE=1
DTYPE=auto
LOG_LEVEL=INFO
```

### C.4 Dockerfile de referencia

Cree un `Dockerfile` junto al `docker-compose.yml`:

```dockerfile
# Dockerfile para CAJAL API
ARG CUDA_VERSION=12.1
FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu22.04

ARG BACKEND=vllm
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git curl wget \
    && rm -rf /var/lib/apt/lists/*

# Crear entorno
WORKDIR /app
COPY scripts/deploy_local_server.py /app/
COPY requirements.txt* /app/ 2>/dev/null || true

# Instalar Python dependencies
RUN pip3 install --no-cache-dir \
    torch>=2.4.0 \
    transformers>=4.45.0 \
    accelerate>=0.34.0 \
    fastapi uvicorn pydantic \
    huggingface_hub

# Instalar backend específico
RUN if [ "$BACKEND" = "vllm" ]; then \
      pip3 install --no-cache-dir vllm>=0.6.0; \
    else \
      CMAKE_ARGS="-DLLAMA_CUDA=on" pip3 install --no-cache-dir llama-cpp-python; \
    fi

# Puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Entrypoint
CMD ["python3", "deploy_local_server.py", \
     "--model", "${MODEL_PATH}", \
     "--type", "${MODEL_TYPE}", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
```

### C.5 Levantar servicio

```bash
cd docker/

# Iniciar
docker compose up -d

# Ver logs
docker compose logs -f api

# Verificar salud
curl http://localhost:8000/health

# Escalar (ejemplo)
docker compose up -d --scale api=1

# Detener
docker compose down

# Detener y eliminar volúmenes
docker compose down -v
```

### C.6 Verificar GPU en contenedor

```bash
docker compose exec api nvidia-smi
```

Debería mostrar la GPU con el proceso de Python/vLLM ejecutándose.

---

## Opción D: Hugging Face Inference API

### D.1 Subir modelo a HuggingFace

```bash
# Usar el script de exportación con --push-to-hf
python scripts/export_to_gguf.py \
  --model ./merged_model \
  --params 14 \
  --output ./gguf_exports \
  --push-to-hf tuusuario/cajal \
  --hf-token $HF_TOKEN

# O subir manualmente con huggingface-cli
huggingface-cli login
cd ./merged_model
huggingface-cli upload tuusuario/cajal .
```

### D.2 Usar Inference Endpoints (HuggingFace Pro)

1. Vaya a [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Cree un token de lectura
3. Vaya a [huggingface.co/inference-endpoints](https://huggingface.co/inference-endpoints)
4. Cree un nuevo endpoint con su modelo
5. Seleccione instancia GPU (ej: NVIDIA A10G)

```python
# Cliente Python
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="tuusuario/cajal",
    token="hf_xxxxxxxx"
)

response = client.chat_completion(
    messages=[
        {"role": "system", "content": "You are CAJAL."},
        {"role": "user", "content": "Explain Sybil attacks."}
    ],
    max_tokens=4096,
    temperature=0.7,
)
print(response.choices[0].message.content)
```

### D.3 API Serverless (Gratuito, limitado)

```python
import requests

API_URL = "https://api-inference.huggingface.co/models/tuusuario/cajal"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

output = query({
    "inputs": "Analyze the legal status of decentralized exchanges.",
    "parameters": {"max_new_tokens": 1024, "temperature": 0.7}
})
```

> **Nota**: El tier gratuito tiene cold-start y límites de rate. Para producción use Inference Endpoints dedicados.

---

## 8. Benchmarking de Velocidad

### 8.1 Script de benchmark incluido

Use el siguiente script para medir tokens/segundo:

```bash
#!/usr/bin/env bash
# benchmark_speed.sh

API_URL="http://localhost:8000/v1/chat/completions"
PROMPT="Explain the prisoner's dilemma in the context of P2P file sharing protocols. Include mathematical notation."

# Warmup
curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hi"}],"max_tokens":10}' > /dev/null

echo "Benchmarking CAJAL..."
echo "Prompt length: $(echo -n "$PROMPT" | wc -c) chars"
echo ""

# Medir tiempo
echo "[1] Non-streaming test"
START=$(date +%s.%N)
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"$PROMPT\"}],\"max_tokens\":2048}")
END=$(date +%s.%N)

TOKENS=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['choices'][0]['message']['content'].split()))")
DURATION=$(python3 -c "print(f'{$END - $START:.2f}')")
TPS=$(python3 -c "print(f'{$TOKENS / ($END - $START):.1f}')")

echo "  Duration: ${DURATION}s"
echo "  Output tokens: $TOKENS"
echo "  Speed: ${TPS} tok/s"
```

### 8.2 Resultados esperados (RTX 3090)

| Formato | VRAM Usada | Contexto 4K | Contexto 16K | Contexto 32K |
|---------|-----------|-------------|--------------|--------------|
| Q4_K_M (GGUF) | ~6 GB | 45-55 tok/s | 35-45 tok/s | 25-35 tok/s |
| Q5_K_M (GGUF) | ~7 GB | 40-50 tok/s | 30-40 tok/s | 22-30 tok/s |
| Q8_0 (GGUF) | ~10 GB | 30-40 tok/s | 22-30 tok/s | 15-22 tok/s |
| F16 (vLLM) | ~18 GB | 55-70 tok/s | 40-55 tok/s | 30-45 tok/s |
| AWQ (vLLM) | ~5 GB | 50-60 tok/s | 40-50 tok/s | 30-40 tok/s |

> **Nota**: Velocidades aproximadas para modelo ~7B parámetros. Modelos 14B son ~40-50% más lentos. Resultados varían según prompt y batch size.

### 8.3 Benchmark con vLLM benchmarks

```bash
# Descargar benchmark de vLLM
python -m vllm.benchmarks.benchmark_throughput \
  --model ./merged_model \
  --input-len 1024 \
  --output-len 2048 \
  --num-prompts 10 \
  --max-model-len 32768
```

---

## 9. Troubleshooting Común

### Problema: `CUDA out of memory`

**Causa**: El modelo no cabe en la VRAM disponible.

**Soluciones**:
```bash
# 1. Usar cuantización más agresiva
python deploy_local_server.py --model ./model-q4.gguf --type gguf

# 2. Reducir context length
python deploy_local_server.py ... --context-length 8192 --max-model-len 8192

# 3. Reducir GPU memory utilization (vLLM)
python deploy_local_server.py ... --gpu-memory-utilization 0.70

# 4. Activar CPU offload (llama-cpp)
# En el código, cambiar n_gpu_layers a un valor menor
```

### Problema: `ollama: command not found`

**Causa**: Ollama no está instalado o no está en PATH.

**Soluciones**:
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows
# Descargar desde https://ollama.com/download/windows
```

### Problema: `llama.cpp/convert_hf_to_gguf.py not found`

**Causa**: Falta llama.cpp instalado.

**Soluciones**:
```bash
# Clonar y compilar
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j$(nproc)

# O usar pre-compilado
pip install llama-cpp-python

# Verificar
which llama-quantize
```

### Problema: `ImportError: cannot import name 'LLM' from 'vllm'`

**Causa**: vLLM no instalado o versión incompatible.

**Soluciones**:
```bash
# Reinstalar vLLM
pip uninstall vllm -y
pip install vllm>=0.6.0

# Verificar compatibilidad CUDA
python -c "import torch; print(torch.version.cuda)"  # Debe ser >= 12.1
```

### Problema: Docker no detecta GPU

**Causa**: NVIDIA Container Toolkit no configurado.

**Soluciones**:
```bash
# Verificar
docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi

# Si falla, reconfigurar
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Problema: Respuestas lentas con Ollama

**Causa**: Ollama puede no estar usando la GPU completamente.

**Soluciones**:
```bash
# Verificar uso de GPU
ollama ps  # Muestra modelos cargados y GPU/CPU

# Forzar GPU layers en Modelfile
# Añadir: PARAMETER num_gpu 999

# Ver logs de Ollama
journalctl -u ollama -f  # Linux
# o
# En macOS/Windows, revisar logs de la app
```

### Problema: El modelo genera texto sin sentido

**Causa**: Chat template incorrecto o modelo no cargado correctamente.

**Soluciones**:
```bash
# Verificar chat template
python -c "from transformers import AutoTokenizer; t=AutoTokenizer.from_pretrained('./model'); print(t.chat_template)"

# Usar chat template correcto para Qwen
python deploy_local_server.py ... --chat-template "qwen-2.5"

# Verificar que el modelo fine-tuned se cargó correctamente
# Revisar los primeros tokens de salida con un prompt simple
```

### Problema: Error de cuantización GGUF

**Causa**: Archivo GGUF corrupto o incompatible.

**Soluciones**:
```bash
# Verificar integridad del GGUF
python -c "from llama_cpp import Llama; m=Llama('model.gguf', n_ctx=512); print('OK')"

# Re-exportar
python export_to_gguf.py --model ./model --params 14 --output ./gguf_exports --quants q4_k_m

# Verificar con llama.cpp directamente
./llama.cpp/llama-cli -m model.gguf -p "Test" -n 10
```

### Problema: No se puede conectar al servidor API

**Causa**: Firewall, binding incorrecto, o servicio no iniciado.

**Soluciones**:
```bash
# Verificar que el proceso escucha
sudo ss -tlnp | grep 8000

# Verificar binding
python deploy_local_server.py ... --host 0.0.0.0  # Escuchar en todas las interfaces

# Abrir puerto en firewall (Ubuntu)
sudo ufw allow 8000/tcp

# Probar localmente primero
curl http://127.0.0.1:8000/health
```

---

## Comandos Rápidos de Despliegue

### Flujo completo recomendado (RTX 3090)

```bash
# 1. Exportar modelo
python scripts/export_to_gguf.py \
  --model ./merged_model \
  --params 14 \
  --output ./gguf_exports \
  --quants q4_k_m q5_k_m

# 2. Desplegar con Ollama (más fácil)
chmod +x scripts/setup_ollama.sh
./scripts/setup_ollama.sh --model-dir ./gguf_exports --quant q4_k_m

# 3. O desplegar API server (más control)
python scripts/deploy_local_server.py \
  --model ./gguf_exports/cajal-q4_k_m.gguf \
  --type gguf \
  --port 8000

# 4. O Docker (más portable)
cd docker/
MODELS_DIR=../gguf_exports MODEL_PATH=/app/models/cajal-q4_k_m.gguf \
  docker compose up -d
```

### Integración con aplicaciones

```python
# OpenAI-compatible client
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",  # o http://localhost:11434/v1 para Ollama
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="cajal",
    messages=[
        {"role": "system", "content": "You are CAJAL."},
        {"role": "user", "content": "Design a Sybil-resistant reputation mechanism."}
    ],
    temperature=0.7,
    max_tokens=4096,
)
print(response.choices[0].message.content)
```

---

## Referencias

- [Unsloth Documentation](https://docs.unsloth.ai/)
- [vLLM Documentation](https://docs.vllm.ai/)
- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/README.md)
- [llama.cpp Wiki](https://github.com/ggerganov/llama.cpp/wiki)
- [GGUF Specification](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index)

---

**CAJAL Team** | *Rigorous research, decentralized thinking.*
