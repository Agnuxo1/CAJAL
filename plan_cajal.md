# Plan Ampliado: CAJAL-4B — Dataset Ecosystem Completo

## Contexto Actualizado
- **Nombre del modelo**: CAJAL + parámetros (CAJAL-4B, CAJAL-8B, etc.)
- **Dataset base**: ~670 papers de P2PCLAW
- **Dataset ampliado**: Papers + Repositorios + Skills + Archivos locales + Recursos externos

## Fuentes de Conocimiento a Incluir

### 1. Papers P2PCLAW (~670 papers)
Ya cubierto en fase anterior.

### 2. Repositorios GitHub (20+ repos)
| Repo | URL | Tipo | Prioridad |
|------|-----|------|-----------|
| p2pclaw-mcp-server | Agnuxo1/p2pclaw-mcp-server | Core API | Alta |
| p2pclaw-unified | Agnuxo1/p2pclaw-unified | Plataforma unificada | Alta |
| OpenCLAW-P2P | Agnuxo1/OpenCLAW-P2P | Frontend/Red P2P | Alta |
| The-Living-Agent | Agnuxo1/The-Living-Agent | Arquitectura agente | Alta |
| P2P-OpenClaw | P2P-OpenClaw (org) | Organización | Media |
| semantic-kernel | Agnuxo1/semantic-kernel | Framework AI | Media |
| best-of-lean4 | Agnuxo1/best-of-lean4 | Recursos Lean 4 | Media |
| EnigmAgent | Agnuxo1/EnigmAgent | Agente especializado | Media |
| benchclaw | Agnuxo1/benchclaw | Benchmark | Alta |
| CognitionBoard | Agnuxo1/CognitionBoard | Visualización | Media |
| AgentBoot-app | Agnuxo1/AgentBoot-app | App de arranque | Media |
| AgentBoot | Agnuxo1/AgentBoot | Framework boot | Media |
| pixelflow | Agnuxo1/pixelflow | Pipeline visual | Media |
| Project-NAVAJO | Agnuxo1/Project-NAVAJO | Proyecto | Media |
| Token-compression | Agnuxo1/Token-compression | Compresión tokens | Alta |
| King-Skill | Agnuxo1/King-Skill | Arquitectura cognitiva | Alta |
| CHIMERA | Agnuxo1/CHIMERA | Motor neuromórfico | Media |
| Universal-Cognitive-Architecture | Agnuxo1/Universal-Cognitive-Architecture | Text-as-Code | Alta |
| OpenCLAW-Autonomous | Agnuxo1/OpenCLAW-Autonomous | Plataforma | Alta |
| p2pclaw | Agnuxo1/p2pclaw | Core | Alta |

### 3. Archivos Locales (El usuario debe copiarlos)
- E:\OpenCLAW-4\papers\Skills\Token-compression.md
- E:\OpenCLAW-4\papers\Skills\Skills-frontier-math-solver.md
- E:\OpenCLAW-4\papers\Skills\king-skill\SKILL.md

### 4. Recursos Externos
- small-diophantine.pdf de epoch.ai/frontiermath

## Stage 1: Recopilación de Repositorios
- Crear script master que clone/ descargue todos los repos
- Extraer contenido clave de cada repo (README, docs, código relevante)
- Filtrar archivos irrelevantes (node_modules, .git, build, etc.)
- Estructurar como contexto para el modelo

## Stage 2: Compilación del Dataset Ampliado
- Crear script que combine: papers + repos + skills + recursos
- Formato de conversación especializado para cada tipo:
  - Papers: "Write a paper on..." → paper
  - Repos: "What does the X module do?" → explicación
  - Skills: "How do I use Token Compression?" → guía
  - Recursos: "Explain the Diophantine problem..." → explicación
- Dataset de "memoria de plataforma": conocimiento sobre p2pclaw.com

## Stage 3: Actualización de Scripts
- Renombrar todo de CAJAL a CAJAL
- Actualizar system prompts para que el modelo sepa que es CAJAL
- Incluir "memoria" de toda la plataforma en los prompts
- Actualizar connector P2PCLAW para que se identifique como CAJAL

## Stage 4: Entrega
- Dataset ampliado compilado
- Scripts actualizados con branding CAJAL
- Guía de integración de repos
