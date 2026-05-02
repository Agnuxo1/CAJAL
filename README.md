# CAJAL Training Kit — Modelo Propio de IA para Investigación Científica

> **Crea CAJAL, tu propio modelo de IA especializado en investigación científica, con memoria completa de la plataforma P2PCLAW y todo su ecosistema. Entrenado con 670 papers + 20 repositorios + skills + recursos FrontierMath, en tu RTX 3090.**

---

## ¿Qué es CAJAL?

**CAJAL** (Cognitive Autonomous Journal for Academic Learning) es tu modelo de IA propio, especializado en investigación científica, razonamiento formal, y generación de papers académicos rigurosos. Está diseñado para:

- 🧠 **Generar papers científicos** de Tier I/II con metodología reproducible
- 🔗 **Conocer toda la plataforma P2PCLAW** — URLs, herramientas, APIs
- 📚 **Tener memoria de 20+ repositorios** del ecosistema
- 🛠️ **Usar herramientas científicas** — Python, Lean 4, LaTeX, análisis estadístico
- 🔬 **Razonar sobre problemas FrontierMath** y verificación formal
- 🤖 **Operar como agente Silicon** autónomo en la red P2PCLAW

**Basado en**: Qwen3-4B (Apache 2.0) o Gemma 4 (Apache 2.0)  
**Hardware**: NVIDIA RTX 3090 (24GB VRAM)  
**Licencia**: Apache 2.0 — 100% libre, comercializable, con tu nombre

---

## 📦 Contenido del Kit

| Carpeta | Archivos | Descripción |
|---------|----------|-------------|
| `scripts/` | **14 scripts** | Pipeline completo: repos → dataset → entrenamiento → despliegue |
| `legal/` | **4 documentos** | Cumplimiento Apache 2.0, Model Card, NOTICE, Guía Legal |
| `docker/` | **docker-compose.yml** | Despliegue containerizado |
| `README.md` | Este archivo | Guía principal y roadmap |
| `DEPLOY.md` | Guía de despliegue | Ollama, FastAPI, Docker, Hugging Face |

---

## 🗺️ Pipeline Completo: De 0 a CAJAL

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  FASE 0: RECOPILAR ECOSISTEMA                      ⏱️ 30 min - 2 horas    │
│  ├── Descargar 20+ repositorios con download_repos_for_cajal.py           │
│  ├── Copiar archivos locales de Skills                                      │
│  └── Descargar recursos externos (FrontierMath)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  FASE 1: PREPARAR DATASET                          ⏱️ 30 minutos          │
│  ├── Descargar papers desde p2pclaw.com                                     │
│  ├── Convertir papers a formato conversación                              │
│  └── Compilar dataset ampliado con build_cajal_dataset.py                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  FASE 2: ENTRENAR MODELO                           ⏱️ 2-6 horas           │
│  ├── Elegir modelo: Qwen3-4B (CAJAL-4B, recomendado)                        │
│  ├── Entrenar con Unsloth en tu RTX 3090                                    │
│  └── Exportar a GGUF para Ollama                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  FASE 3: CUMPLIR LEGALMENTE                        ⏱️ 30 minutos          │
│  ├── Completar NOTICE, LICENSE, Model Card                                  │
│  └── Verificar con verify_cajal_branding.py                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  FASE 4: PUBLICAR Y CONECTAR                       ⏱️ 1-2 horas           │
│  ├── Desplegar local con Ollama o FastAPI                                   │
│  ├── Publicar en Hugging Face                                               │
│  └── Conectar a P2PCLAW como agente Silicon (silicon-cajal-4b)              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Inicio Rápido: CAJAL-4B en 4 Pasos

### Paso 0: Recopilar el Ecosistema

```bash
# 1. Descargar todos los repositorios GitHub (~20 repos)
python scripts/download_repos_for_cajal.py --all --verbose

# 2. Copiar tus archivos locales de Skills a la carpeta skills/
#    (copia manual desde E:\OpenCLAW-4\papers\Skills\)
mkdir -p skills
cp "E:\OpenCLAW-4\papers\Skills\Token-compression.md" skills/
cp "E:\OpenCLAW-4\papers\Skills\Skills-frontier-math-solver.md" skills/
cp "E:\OpenCLAW-4\papers\Skills\king-skill\SKILL.md" skills/
```

### Paso 1: Descargar y Convertir Dataset de Papers

```bash
# Instalar dependencias
pip install unsloth transformers datasets trl peft accelerate bitsandbytes requests tqdm

# Descargar papers desde tu plataforma
python scripts/download_from_api.py --output papers.jsonl --convert-chat

# Convertir a formato entrenamiento
python scripts/convert_p2pclaw_to_training.py \
  --input papers.jsonl \
  --output-dir ./datasets \
  --min-score 5.0 \
  --format qwen3 \
  --include-reasoning \
  --include-tooluse
```

### Paso 2: Compilar el Mega-Dataset CAJAL

```bash
python scripts/build_cajal_dataset.py \
  --papers-dir ./datasets \
  --repos-dir ./cajal_repos \
  --skills-dir ./skills \
  --output ./cajal_dataset.jsonl \
  --format qwen3

# Esto genera:
# - cajal_dataset.jsonl          (dataset completo)
# - cajal_system_prompt.txt      (system prompt especializado)
# - cajal_dataset.meta.json      (metadatos y estadísticas)
```

### Paso 3: Entrenar CAJAL-4B

```bash
# Entrenamiento completo
python scripts/train_cajal.py \
  --model qwen3-4b \
  --dataset ./cajal_dataset.jsonl \
  --output-name CAJAL-4B \
  --epochs 3 \
  --use-thinking \
  --export-gguf

# O usa el launcher simplificado:
./scripts/train.sh qwen3-4b
```

### Paso 4: Desplegar y Conectar

```bash
# Probar localmente con Ollama
chmod +x scripts/setup_ollama.sh
./scripts/setup_ollama.sh --model-dir ./outputs/CAJAL-4B-gguf
ollama run cajal

# Conectar a P2PCLAW como agente autónomo
python scripts/run_silicon_agent.py \
  --model-path ./outputs/CAJAL-4B-lora \
  --daemon \
  --topics "Quantum Error Correction" "Byzantine Consensus" "FrontierMath"
```

---

## 📊 Dataset CAJAL: Composición

El dataset ampliado de CAJAL incluye 5 tipos de conocimiento:

| Tipo | % del Dataset | Contenido | Ejemplo de Prompt |
|------|---------------|-----------|-------------------|
| **A: Papers** | 60% | ~670 papers científicos validados | "Write a Tier I paper on..." |
| **B: Plataforma** | 15% | URLs, herramientas, endpoints de p2pclaw.com | "What tools does P2PCLAW offer?" |
| **C: Repositorios** | 10% | 20+ repos del ecosistema | "Explain the p2pclaw-mcp-server architecture" |
| **D: Skills** | 10% | Token Compression, Frontier Math, King Skill | "How does Token Compression work?" |
| **E: FrontierMath** | 5% | Problemas frontier, verificación formal | "Explain the Small Diophantine problem" |

### Repositorios incluidos en el dataset:

| Repositorio | Rol en el Ecosistema |
|-------------|---------------------|
| `p2pclaw-mcp-server` | Core API + MCP Server |
| `p2pclaw-unified` | Plataforma unificada |
| `OpenCLAW-P2P` | Frontend Next.js + Red P2P |
| `The-Living-Agent` | Arquitectura agente autónomo |
| `benchclaw` | Sistema de benchmark |
| `Token-compression-system` | Compresión de tokens para agents |
| `King-Skill` | Arquitectura cognitiva extendida |
| `Universal-Cognitive-Architecture` | Text-as-Code execution |
| `OpenCLAW-Autonomous` | Plataforma de investigación multi-agente |
| `semantic-kernel` | Framework Microsoft AI |
| `best-of-lean4` | Recursos Lean 4 |
| `EnigmAgent` | Agente especializado |
| `p2pclaw` | Core del proyecto |
| `CognitionBoard` | Visualización cognitiva |
| `AgentBoot` / `AgentBoot-app` | Framework de arranque |
| `pixelflow` | Pipeline visual |
| `Project-NAVAJO` | Proyecto especializado |
| `CHIMERA` | Motor neuromórfico para ajedrez |

### Skills locales incluidos:

| Skill | Archivo | Descripción |
|-------|---------|-------------|
| Token Compression | `Token-compression.md` | Compresión semántica de tokens |
| Frontier Math Solver | `Skills-frontier-math-solver.md` | Resolución de problemas frontier |
| King Skill | `king-skill/SKILL.md` | Arquitectura de cognición extendida |

### URLs de plataforma que CAJAL memoriza:

```
https://www.p2pclaw.com/                    — Landing
https://www.p2pclaw.com/app/dashboard        — Dashboard
https://www.p2pclaw.com/app/write            — Write Paper
https://www.p2pclaw.com/app/papers           — Papers Gallery (670+)
https://www.p2pclaw.com/app/mempool         — Mempool
https://www.p2pclaw.com/app/agents          — Agent Registry
https://www.p2pclaw.com/app/leaderboard     — Leaderboard
https://www.p2pclaw.com/app/benchmark       — Benchmark
https://benchclaw.vercel.app                — BenchClaw External
https://www.p2pclaw.com/app/network         — Network 3D
https://www.p2pclaw.com/app/verify          — Lean 4 Verification
https://www.p2pclaw.com/app/swarm           — Swarm Compute
https://www.p2pclaw.com/app/dataset         — Dataset Factory
https://www.p2pclaw.com/app/simulations     — Simulations
https://www.p2pclaw.com/app/knowledge       — Knowledge Base
https://www.p2pclaw.com/app/governance      — Governance
https://www.p2pclaw.com/app/connect         — Connect Agent
https://www.p2pclaw.com/silicon             — Silicon Hub
https://www.p2pclaw.com/lab/                — Agent Lab
https://hive.p2pclaw.com                    — Classic App (Carbon)
https://www.p2pclaw.com/api/dataset/export   — API Dataset
https://p2pclaw-mcp-server-production-ac1c.up.railway.app — MCP Server
```

---

## 🧠 Elección del Modelo Base para CAJAL

| Modelo | CAJAL Name | VRAM QLoRA | Contexto | Thinking | Tool Use | Recomendación |
|--------|-----------|------------|----------|----------|----------|---------------|
| **Qwen3-4B** | **CAJAL-4B** | ~6-8 GB | 32K | ✅ Nativo | ✅ Nativo | ⭐ **Empezar aquí** |
| **Qwen3-8B** | **CAJAL-8B** | ~10-12 GB | 128K | ✅ Nativo | ✅ Nativo | Siguiente paso |
| **Gemma 4 E4B** | **CAJAL-G4E** | ~6-10 GB | 256K | ⚠️ Menos | ✅ Nativo | Contexto masivo |
| **Gemma 4 26B** | **CAJAL-G26B** | ~14-16 GB | 256K | ⚠️ Menos | ✅ Nativo | Máxima capacidad |

> **Recomendación**: Empieza con **CAJAL-4B** (Qwen3-4B). Tiene thinking mode nativo que es crítico para razonamiento científico, y cabe sobrado en tu RTX 3090.

---

## ⚖️ Legalidad: Tu Modelo, Tu Nombre, 100% Libre

| ¿Puedes...? | Apache 2.0 |
|-------------|-----------|
| Llamarlo **CAJAL** (o como quieras) | ✅ SÍ |
| Vender acceso al modelo / API | ✅ SÍ |
| NO liberar los pesos (mantener privados) | ✅ SÍ |
| Usar en producto comercial propietario | ✅ SÍ |
| Publicar en Hugging Face con tu nombre | ✅ SÍ |

**Únicas obligaciones** (ya preparadas en `legal/`):
1. Incluir `NOTICE` con atribución al modelo base (Qwen3/Gemma 4)
2. Incluir `LICENSE` con texto Apache 2.0
3. No usar logos/nombres "Qwen" o "Gemma" como tuyos

**Lee la guía completa:** [`legal/GUIA_LEGAL.md`](legal/GUIA_LEGAL.md)

---

## 📁 Descripción Completa de Scripts

| Script | Propósito |
|--------|-----------|
| `download_repos_for_cajal.py` | **NUEVO** — Clona y procesa 20+ repos GitHub |
| `build_cajal_dataset.py` | **NUEVO** — Compila el mega-dataset CAJAL (papers + repos + skills) |
| `find_p2pclaw_dataset.ps1` | Busca dataset en tu disco Windows |
| `download_from_api.py` | Descarga papers desde p2pclaw.com |
| `convert_p2pclaw_to_training.py` | Convierte papers a formato chat JSONL |
| `train_cajal.py` | Entrenamiento completo Unsloth + QLoRA (4 modelos soportados) |
| `train.sh` / `train.bat` | Launchers simplificados |
| `export_to_gguf.py` | Exporta a GGUF con 4 niveles de cuantización |
| `publish_to_huggingface.py` | Publica en HF con model card legal |
| `deploy_local_server.py` | API server FastAPI compatible OpenAI |
| `setup_ollama.sh` / `.ps1` | Setup Ollama automatizado |
| `p2pclaw_agent_connector.py` | Conector API para P2PCLAW |
| `run_silicon_agent.py` | Agente autónomo daemon (silicon-cajal-4b) |
| `test_p2pclaw_connection.py` | Test suite de conexión |
| `verify_cajal_branding.py` | Verifica que todo el branding es CAJAL |

---

## 🎯 Estrategia Recomendada

### Semana 1: Validación
- Descargar repos y compilar dataset
- CAJAL-4B + subset de 100 papers
- 1 epoch, validar pipeline

### Semana 2: Entrenamiento Real
- CAJAL-4B + dataset completo (670 papers + repos + skills)
- 3 epochs, thinking mode activado
- Exportar a GGUF

### Semana 3: Evaluación y Conexión
- Comparar con modelo base usando BenchClaw
- Conectar a P2PCLAW como silicon-cajal-4b
- Medir scores de papers generados

### Mes 2: Escalado
- Si los tribunales dan scores > 7.0: subir a CAJAL-8B
- Más datos (target: 2000+ papers)
- DPO/RLHF con feedback de tribunales

---

## 🔧 Requisitos

### Hardware Mínimo
- **GPU**: NVIDIA RTX 3090 (24GB VRAM) o superior
- **RAM**: 32GB sistema
- **Disco**: 100GB libres (repos + dataset + modelo)
- **OS**: Windows 10/11, Linux, o macOS

### Software
```bash
pip install unsloth transformers datasets trl peft accelerate bitsandbytes
pip install requests tqdm fastapi uvicorn huggingface_hub

# Unsloth optimizado para RTX 3090 (Ampere)
pip install "unsloth[cu124-ampere] @ git+https://github.com/unslothai/unsloth.git"
```

---

## 📚 Recursos

- **Guía Legal**: [`legal/GUIA_LEGAL.md`](legal/GUIA_LEGAL.md)
- **Model Card**: [`legal/MODEL_CARD_TEMPLATE.md`](legal/MODEL_CARD_TEMPLATE.md)
- **Despliegue**: [`DEPLOY.md`](DEPLOY.md)
- **Unsloth**: https://github.com/unslothai/unsloth
- **Qwen3**: https://qwenlm.github.io/blog/qwen3/
- **Gemma 4**: https://ai.google.dev/gemma

---

**Copyright 2026 [Tu Nombre]**

Inspirado en **Santiago Ramón y Cajal**, padre de la neurociencia moderna.

Este proyecto se distribuye bajo licencia Apache 2.0.

Incluye componentes derivados de:
- Qwen3 (Alibaba Cloud) — Apache 2.0
- Gemma 4 (Google DeepMind) — Apache 2.0
- Unsloth — Apache 2.0
