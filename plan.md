# Plan: Crear CAJAL Model

## Objetivo
Crear un modelo de IA propio con branding P2PClaw, especializado en investigación científica, reasoning, y tool use, entrenado con el dataset de ~700 papers de la plataforma, usando una RTX 3090.

## Stage 1: Investigación y Análisis
- Explorar repositorios GitHub (p2pclaw-mcp-server, OpenCLAW-P2P)
- Analizar la plataforma p2pclaw.com (papers, dataset, API endpoints)
- Investigar modelos disponibles en 2026: Qwen3-4B/8B, Gemma 4 E4B/26B, Mistral Small 3, Phi-4
- Verificar licencias Apache 2.0 y requisitos legales
- Buscar mejores prácticas de fine-tuning en RTX 3090 (24GB VRAM)

## Stage 2: Evaluación de Dataset
- El usuario tiene el proyecto en E:\OpenCLAW-4 (local, no accesible desde aquí)
- El dataset se guarda automáticamente en formato JSON adecuado
- Hay copias en Cloudflare y Railway
- API endpoint: /api/dataset/export
- Preparar scripts para que el usuario pueda encontrar y validar el dataset en su local
- Preparar script de conversión a formato de entrenamiento (chat/JSONL)

## Stage 3: Diseño del Modelo y Estrategia Legal
- Elegir modelo base: Qwen3-4B (thinking mode, tool use, context 32K, Apache 2.0)
- Crear guía legal completa: Apache 2.0 requirements, attribution, model card
- Diseñar naming: CAJAL-1B (o similar)
- Plan de despliegue: Hugging Face, Ollama, API propia

## Stage 4: Scripts de Entrenamiento
- Script de fine-tuning con Unsloth + QLoRA en RTX 3090
- Script de conversión de dataset a formato chat
- Script de exportación a GGUF (Ollama/lm Studio)
- Script de conexión a P2PCLAW como agente Silicon
- Script de tool use (Python, Lean 4, LaTeX)

## Stage 5: Material de Entrega
- Guía completa paso a paso (documento)
- Scripts listos para usar
- Model card template
- Connector API para P2PCLAW
- Checklist legal de cumplimiento Apache 2.0

## Skills a cargar
- report-writing: Para generar la guía completa de entrenamiento
- vibecoding-general-swarm: Para crear scripts y código
