---
language:
- en
- es
- zh
- de
- fr
license: apache-2.0
library_name: transformers
tags:
- ollama
- gguf
- transformers
- safetensors
- qwen3.5
- causal-lm
- lora
- qlora
- text-generation
- conversational
- agent
- scientific-research
- peer-to-peer
- crypto-law
- p2pclaw
- fine-tuned
base_model: Qwen/Qwen3.5-4B
pipeline_tag: text-generation
model_type: qwen3
quantization:
- bitsandbytes-nf4
inference: true
widget:
- text: "Write a scientific paper about decentralized governance in P2P networks"
  example_title: "Paper Writing"
- text: "Analyze this consensus mechanism using game theory"
  example_title: "Research Analysis"
extra_gated_prompt: 'false'
---

# CAJAL-4B-P2PCLAW

> Autonomous Scientific Research Agent — Fine-tuned from Qwen3.5-4B for the P2PCLAW ecosystem

[![GitHub](https://img.shields.io/badge/GitHub-Agnuxo1%2FCAJAL-181717?logo=github)](https://github.com/Agnuxo1/CAJAL)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Agnuxo%2FCAJAL--4B--P2PCLAW-blue?logo=huggingface)](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW)
[![PyPI](https://img.shields.io/badge/PyPI-cajal-blue?logo=pypi)](https://pypi.org/project/cajal/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://github.com/Agnuxo1/CAJAL/blob/main/LICENSE)

## Overview

**CAJAL-4B-P2PCLAW** is a fine-tuned language model specialized in autonomous scientific research and paper writing within the P2PCLAW (Peer-to-Peer Crypto Law) ecosystem. Built on top of [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) using QLoRA (4-bit NF4 quantization with LoRA adapters), it follows a rigorous 14-step paper-writing procedure that includes arXiv review, P2PCLAW rule compliance, claim verification, and Lean4 proof checking.

### Key Features

- **14-Step Paper Writing Procedure**: Intent analysis → arXiv review → draft → compliance check → API enrichment → plan → verify claims → real data → test code → write paper → Lean4 verify → submit → score
- **P2PCLAW Integration**: Native understanding of P2PCLAW rules, constitution, and submission workflows
- **Game-Theoretic Analysis**: Specialized in game theory, consensus mechanisms, and distributed systems
- **Multi-format Output**: Generates LaTeX papers, Python code, Lean4 proofs, and structured analysis

## Quick Start

### Using with 🤗 Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "Agnuxo/CAJAL-4B-P2PCLAW",
    trust_remote_code=True,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("Agnuxo/CAJAL-4B-P2PCLAW")

messages = [
    {"role": "system", "content": "You are CAJAL-4B, an autonomous research agent..."},
    {"role": "user", "content": "Write a paper about Nash equilibria in blockchain governance"}
]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=4096)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Using with 🦙 Ollama

```bash
# Install Ollama from https://ollama.com
ollama run agnuxo/cajal-4b-p2pclaw

# Or create from Modelfile:
curl -O https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW/resolve/main/Modelfile
ollama create cajal-4b -f Modelfile
ollama run cajal-4b
```

### Using with 🖥️ LM Studio

1. Download the GGUF quantized version from [the Files tab](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW/tree/main)
2. Open LM Studio → File → Import Model → Select the `.gguf` file
3. Start chatting!

### Using with llama.cpp

```bash
# Download GGUF file
wget https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW/resolve/main/cajal-4b-p2pclaw-Q4_K_M.gguf

# Run inference
./llama-cli -m cajal-4b-p2pclaw-Q4_K_M.gguf -p "Write a paper about..." -ngl 32
```

### Using with vLLM

```python
from vllm import LLM, SamplingParams

llm = LLM(model="Agnuxo/CAJAL-4B-P2PCLAW", trust_remote_code=True)
params = SamplingParams(max_tokens=4096, temperature=0.7)
output = llm.generate("Write a scientific paper about decentralized governance", params)
print(output[0].outputs[0].text)
```

### Using with Python (pip)

```bash
pip install cajal
cajal chat  # Interactive CLI
cajal serve # OpenAI-compatible API server on port 8765
```

### Using with API (OpenAI-compatible)

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8765/v1",
    api_key="cajal"
)
response = client.chat.completions.create(
    model="cajal-4b",
    messages=[{"role": "user", "content": "Analyze Nash equilibria in P2P networks"}]
)
print(response.choices[0].message.content)
```

## Model Details

| Property | Value |
|---|---|
| **Base Model** | Qwen3.5-4B |
| **Architecture** | Qwen3ForCausalLM (Hybrid linear attention + self-attention) |
| **Parameters** | ~4B total, 25.2M trainable (LoRA) |
| **Quantization** | 4-bit NF4 (BitsAndBytes) |
| **LoRA Rank** | r=16, α=32 |
| **Training Dataset** | P2PCLAW corpus (135 agent workflow + 669 full + 487 HQ + 1,461 reasoning examples) |
| **Context Length** | 32K tokens |
| **Training Hardware** | RTX 3090 24GB |
| **Training Time** | 769 minutes (3 epochs) |
| **Final Loss** | 0.03192 |
| **Accuracy** | 98.95% |

## Training Configuration

```yaml
base_model: Qwen3.5-4B
quantization: 4-bit NF4 (BitsAndBytes)
lora_rank: 16
lora_alpha: 32
lora_dropout: 0.05
target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
learning_rate: 2e-4
epochs: 3
batch_size: 1
gradient_accumulation: 4
max_seq_length: 4096
optimizer: paged_adamw_8bit
scheduler: cosine
warmup_ratio: 0.1
```

## Ecosystem

CAJAL-4B-P2PCLAW is part of a complete ecosystem:

| Component | Description | Link |
|---|---|---|
| 🐍 Python Package | `pip install cajal` — CLI, API server, desktop | [PyPI](https://pypi.org/project/cajal/) |
| 🌐 Browser Extension | Chrome, Firefox, Edge sidebar | [GitHub](https://github.com/Agnuxo1/CAJAL/tree/main/ecosystem/browser-extension) |
| 📝 VS Code Extension | In-editor assistance | [GitHub](https://github.com/Agnuxo1/CAJAL/tree/main/ecosystem/vscode-extension) |
| 🖥️ Desktop App | System tray + chat interface | [GitHub](https://github.com/Agnuxo1/CAJAL/tree/main/src/cajal/desktop.py) |
| 🔌 API Server | OpenAI-compatible (port 8765) | [GitHub](https://github.com/Agnuxo1/CAJAL/tree/main/src/cajal/server.py) |

### Integration Guides

- [OpenClaw](https://github.com/Agnuxo1/CAJAL/blob/main/ecosystem/integrations/openclaw.md)
- [Hermes](https://github.com/Agnuxo1/CAJAL/blob/main/ecosystem/integrations/hermes.md)
- [Kilocode](https://github.com/Agnuxo1/CAJAL/blob/main/ecosystem/integrations/kilocode.md)
- [Codex CLI](https://github.com/Agnuxo1/CAJAL/blob/main/ecosystem/integrations/codex-cli.md)
- [Cursor](https://github.com/Agnuxo1/CAJAL/blob/main/ecosystem/integrations/cursor.md)
- [Windsurf](https://github.com/Agnuxo1/CAJAL/blob/main/ecosystem/integrations/windsurf.md)
- [LM Studio](https://github.com/Agnuxo1/CAJAL/blob/main/ecosystem/integrations/lm-studio.md)
- [Ollama](https://github.com/Agnuxo1/CAJAL/blob/main/ecosystem/integrations/ollama.md)
- [Pinokio](https://github.com/Agnuxo1/CAJAL/blob/main/ecosystem/integrations/pinokio.md)

## System Prompt

The model uses a specialized 14-step paper-writing procedure:

```
You are CAJAL-4B, an autonomous scientific research agent specializing in 
peer-to-peer network architectures, crypto-legal frameworks, game-theoretic 
consensus mechanisms, and distributed systems.

STEP 1: Understand the user's intent
STEP 2: Review arXiv for related work
STEP 3: Draft initial paper structure
STEP 4: Check P2PCLAW compliance
STEP 5: Enrich using APIs (Semantic Scholar, etc.)
STEP 6: Plan final paper structure
STEP 7: Verify all claims with citations
STEP 8: Suggest real data sources
STEP 9: Write test code for validation
STEP 10: Write the complete paper in LaTeX
STEP 11: Verify with Lean4 if applicable
STEP 12: Submit to P2PCLAW
STEP 13: Score and evaluate
STEP 14: Provide feedback for improvement
```

The full system prompt is available in [`cajal_9b_system_prompt.txt`](https://github.com/Agnuxo1/CAJAL/blob/main/cajal_9b_system_prompt.txt).

## Limitations & Biases

- Trained on P2PCLAW-specific data — may not generalize well to unrelated domains
- 4-bit quantization introduces slight accuracy degradation vs full precision
- Maximum context length of 4096 tokens during training (32K at inference)
- English and Spanish primary; other languages may have reduced quality
- The model follows P2PCLAW-specific rules and constitution by design

## Citation

```bibtex
@misc{cajal4b2026,
  title={CAJAL-4B-P2PCLAW: Autonomous Scientific Research Agent},
  author={Agnuxo},
  year={2026},
  publisher={HuggingFace},
  url={https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW}
}
```

## License

Apache License 2.0 — See [LICENSE](https://github.com/Agnuxo1/CAJAL/blob/main/LICENSE) for details.

## Acknowledgments

- Base model: [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) by Alibaba Cloud
- Training framework: [Transformers](https://github.com/huggingface/transformers) + [PEFT](https://github.com/huggingface/peft) + [BitsAndBytes](https://github.com/TimDettmers/bitsandbytes)
- P2PCLAW ecosystem: [P2PCLAW](https://p2pclaw-mcp-server-production-ac1c.up.railway.app)