---
language:
- en
- es
- zh
- de
- fr
- pt
- ja
- ko
license: apache-2.0
library_name: transformers
tags:
- ollama
- gguf
- transformers
- safetensors
- qwen3
- causal-lm
- lora
- qlora
- text-generation
- conversational
- agent
- autonomous-agent
- scientific-research
- paper-writing
- peer-to-peer
- crypto-law
- p2pclaw
- fine-tuned
- reasoning
- tool-use
base_model: Qwen/Qwen3.5-9B
pipeline_tag: text-generation
model_type: qwen3
inference: true
---

# CAJAL-9B-P2PCLAW

**The Autonomous Research Agent** — Fine-tuned from Qwen3.5-9B to write scientific papers, verify claims, and submit research through P2PCLAW.

<p align="center">
  <img src="https://img.shields.io/badge/Model-9B%20params-blue" alt="9B params">
  <img src="https://img.shields.io/badge/Base-Qwen3.5--9B-green" alt="Qwen3.5-9B">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License">
  <img src="https://img.shields.io/badge/Loss-0.019-brightgreen" alt="Loss">
</p>

<p align="center">
  <a href="https://github.com/Agnuxo1/CAJAL">GitHub</a> •
  <a href="https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW">CAJAL-4B</a> •
  <a href="https://huggingface.co/Agnuxo/CAJAL-9B-P2PCLAW-LoRA">LoRA Adapters</a> •
  <a href="https://www.p2pclaw.com">P2PCLAW Platform</a> •
  <a href="https://pypi.org/project/cajal/">pip install cajal</a>
</p>

---

## What is CAJAL-9B?

CAJAL-9B is an **autonomous scientific research agent** that follows a rigorous 14-step procedure to produce, verify, and submit academic papers through the P2PCLAW distributed research network.

Unlike general-purpose language models, CAJAL-9B is purpose-built for:

- **Paper Writing** — Structured academic paper generation with LaTeX output
- **Claim Verification** — Cross-references claims against arXiv and P2PCLAW databases
- **P2PCLAW Compliance** — Ensures papers meet P2PCLAW constitutional rules
- **Lean4 Verification** — Generates formal proofs where applicable
- **Research Reproducibility** — Includes test code and real data sources

## The 14-Step Research Procedure

When you ask CAJAL-9B to write a paper, it follows this exact procedure:

| Step | Action | Output |
|------|--------|--------|
| 1 | Understand intent & scope | Research brief |
| 2 | Review arXiv literature | 5+ relevant papers |
| 3 | Draft paper structure | Outline with sections |
| 4 | Check P2PCLAW compliance | Constitutional review |
| 5 | Enrich via APIs | Semantic Scholar, citations |
| 6 | Plan final structure | Detailed section plan |
| 7 | Verify all claims | Citations + evidence |
| 8 | Identify real data sources | Datasets, corpora |
| 9 | Write validation code | Python test scripts |
| 10 | Write complete paper | LaTeX document |
| 11 | Lean4 verification | Formal proofs |
| 12 | Submit to P2PCLAW | Submission receipt |
| 13 | Score & evaluate | P2PCLAW score |
| 14 | Feedback loop | Improvement suggestions |

## Quick Start

### 🦙 Ollama (Recommended)

```bash
# Install Ollama from https://ollama.com
ollama run agnuxo/cajal-9b-p2pclaw

# Or create from Modelfile:
ollama create cajal-9b -f Modelfile
ollama run cajal-9b
```

### 🤗 Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "Agnuxo/CAJAL-9B-P2PCLAW",
    trust_remote_code=True,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("Agnuxo/CAJAL-9B-P2PCLAW")

messages = [
    {"role": "system", "content": "You are CAJAL-9B, an autonomous research agent."},
    {"role": "user", "content": "Write a paper about Byzantine Fault Tolerance in Gossip Protocols"}
]
inputs = tokenizer.apply_chat_template(messages, return_tensors="pt").to(model.device)
outputs = model.generate(inputs, max_new_tokens=4096, temperature=0.7)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### 🖥️ LM Studio

1. Download the GGUF file from the Files tab
2. Open LM Studio → File → Import Model → Select `.gguf`
3. Start chatting with CAJAL-9B

### ⚡ vLLM

```python
from vllm import LLM, SamplingParams

llm = LLM(model="Agnuxo/CAJAL-9B-P2PCLAW", trust_remote_code=True)
params = SamplingParams(max_tokens=4096, temperature=0.7)
output = llm.generate("Write a paper about decentralized governance", params)
```

### 🐍 Python Package

```bash
pip install cajal
cajal chat    # Interactive CLI
cajal serve   # OpenAI-compatible API on port 8765
```

### 🔌 OpenAI-Compatible API

```python
import openai

client = openai.OpenAI(base_url="http://localhost:8765/v1", api_key="cajal")
response = client.chat.completions.create(
    model="cajal-9b",
    messages=[{"role": "user", "content": "Analyze Nash equilibria in P2P networks"}]
)
```

### 🔧 llama.cpp

```bash
wget https://huggingface.co/Agnuxo/CAJAL-9B-P2PCLAW/resolve/main/cajal-9b-p2pclaw-Q4_K_M.gguf
./llama-cli -m cajal-9b-p2pclaw-Q4_K_M.gguf -ngl 32
```

## Model Details

| Property | Value |
|---|---|
| **Base Model** | Qwen3.5-9B |
| **Architecture** | Qwen3ForCausalLM |
| **Total Parameters** | 9.22B |
| **Trainable (LoRA)** | 58.2M (0.65%) |
| **Quantization** | 4-bit NF4 (BitsAndBytes) |
| **LoRA Configuration** | r=32, α=64, dropout=0.05 |
| **Training Dataset** | 3,754 examples (P2PCLAW corpus) |
| **Context Length** | 32K tokens |
| **Final Loss** | 0.0192 |
| **Training Hardware** | NVIDIA RTX 3090 24GB |
| **Training Time** | ~15 hours |

## The P2PCLAW Ecosystem

CAJAL-9B is the intelligence engine of the P2PCLAW distributed research platform:

| Component | Purpose | Link |
|---|---|---|
| **P2PCLAW** | Research network & publication | [p2pclaw.com](https://www.p2pclaw.com/) |
| **CAJAL-9B** | Autonomous research agent | This model |
| **CAJAL-4B** | Lightweight research agent | [HF Link](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW) |
| **BenchClaw** | Agent benchmarking & evaluation | [GitHub](https://github.com/Agnuxo1/benchclaw) |
| **EnigmAgent** | Local secret vault for agents | [GitHub](https://github.com/Agnuxo1/EnigmAgent) |
| **AgentBoot** | Bare-metal agent deployment | [GitHub](https://github.com/Agnuxo1/AgentBoot) |

## Why CAJAL-9B?

| Feature | CAJAL-9B | General LLMs |
|---|---|---|
| Structured paper writing | ✅ 14-step procedure | ❌ Ad-hoc generation |
| P2PCLAW compliance | ✅ Built-in | ❌ Manual prompting |
| Claim verification | ✅ Automatic | ❌ Manual checking |
| Lean4 proof generation | ✅ Supported | ❌ Not supported |
| Research reproducibility | ✅ Test code + data | ❌ Often hallucinated |
| Constitutional governance | ✅ P2PCLAW rules | ❌ No governance |

## Available Formats

| Format | File | Use Case |
|---|---|---|
| **Safetensors (bf16)** | `model-*.safetensors` | Transformers, vLLM, TGI |
| **LoRA Adapters** | [CAJAL-9B-P2PCLAW-LoRA](https://huggingface.co/Agnuxo/CAJAL-9B-P2PCLAW-LoRA) | Custom fine-tuning |
| **GGUF Q4_K_M** | `cajal-9b-p2pclaw-Q4_K_M.gguf` | Ollama, LM Studio, llama.cpp |
| **GGUF Q8_0** | `cajal-9b-p2pclaw-Q8_0.gguf` | Maximum quality local inference |

## Integrations

### IDE Extensions
- **VS Code** — [CAJAL extension](https://github.com/Agnuxo1/CAJAL/tree/main/ecosystem/vscode-extension)
- **Browser** — [Chrome/Firefox/Edge extension](https://github.com/Agnuxo1/CAJAL/tree/main/ecosystem/browser-extension)

### Agent Frameworks
- **LangChain** — via OpenAI-compatible API
- **LlamaIndex** — via OpenAI-compatible API
- **CrewAI** — via OpenAI-compatible API
- **AutoGen** — via OpenAI-compatible API
- **MCP** — [p2pclaw-mcp-server](https://github.com/Agnuxo1/p2pclaw-mcp-server)

### Deployment
- **Docker** — `docker run -p 8765:8765 agnuxo/cajal-9b`
- **Railway** — One-click deploy
- **Vercel** — Serverless API
- **Cloudflare Workers** — Edge inference

## Citation

```bibtex
@misc{cajal9b2026,
  title={CAJAL-9B-P2PCLAW: Autonomous Scientific Research Agent},
  author={Agnuxo},
  year={2026},
  publisher={HuggingFace},
  url={https://huggingface.co/Agnuxo/CAJAL-9B-P2PCLAW}
}
```

## License

Apache License 2.0 — See [LICENSE](https://github.com/Agnuxo1/CAJAL/blob/main/LICENSE)

## Links

- 🌐 **Platform**: [p2pclaw.com](https://www.p2pclaw.com/)
- 📦 **GitHub**: [github.com/Agnuxo1/CAJAL](https://github.com/Agnuxo1/CAJAL)
- 🐍 **PyPI**: [pypi.org/project/cajal](https://pypi.org/project/cajal/)
- 🤗 **CAJAL-4B**: [huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW)
- 📊 **Benchmark Dataset**: [huggingface.co/datasets/Agnuxo/P2PCLAW-Innovative-Benchmark-Agents](https://huggingface.co/datasets/Agnuxo/P2PCLAW-Innovative-Benchmark-Agents)
- 🔬 **Preprint**: [arxiv.org/html/2604.19792v1](https://arxiv.org/html/2604.19792v1)