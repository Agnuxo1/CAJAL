# CAJAL-9B with llama.cpp

## Overview

**CAJAL-9B** is a specialized 9B parameter model for generating structured scientific papers locally. It is a finetune of **Qwen3.6-9B-Instruct**, optimized for academic content generation with structured sections (Abstract, Introduction, Methods, Results, Conclusions).

## Model Specs

| Parameter | Value |
|-----------|-------|
| Base Model | Qwen3.6-9B-Instruct |
| Parameters | 9B |
| GGUF Size (Q4_K_M) | ~4.5GB |
| GGUF Size (Q5_K_M) | ~5.5GB |
| Context Length | 32K tokens |
| Special Tokens | [ABSTRACT], [INTRO], [METHODS], [RESULTS], [CONCLUSIONS] |

## Download

From HuggingFace:
```bash
# Download GGUF directly
huggingface-cli download Agnuxo/CAJAL-9B-P2PCLAW --include "*.gguf"

# Or download the entire repo
huggingface-cli download Agnuxo/CAJAL-9B-P2PCLAW --local-dir ./cajal-9b
```

## Usage with llama-cli

### Basic text generation
```bash
llama-cli -m cajal-9b-q4_k_m.gguf \
  -p "Generate a scientific paper about climate change modeling:" \
  -n 2048 \
  --temp 0.3 \
  --top-p 0.8 \
  --top-k 40 \
  --repeat-penalty 1.1
```

### Conversation mode with custom template
```bash
llama-cli -m cajal-9b-q4_k_m.gguf -cnv \
  --chat-template chatml \
  --in-prefix "Topic: " \
  --in-suffix "\nPaper:"
```

### Server mode (OpenAI-compatible API)
```bash
llama-server -m cajal-9b-q4_k_m.gguf \
  --port 8080 \
  --host 0.0.0.0 \
  --ctx-size 32768
```

Then query via curl:
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cajal-9b",
    "messages": [
      {"role": "system", "content": "You are CAJAL-9B, a scientific paper generation assistant."},
      {"role": "user", "content": "Write a paper about renewable energy storage"}
    ],
    "temperature": 0.3,
    "max_tokens": 2048
  }'
```

## Grammar-Constrained Output

CAJAL supports structured paper generation via GBNF grammars:

```bash
llama-cli -m cajal-9b-q4_k_m.gguf \
  -p "Generate a paper structure:" \
  --grammar-file grammars/json.gbnf \
  -n 512
```

Example grammar for paper sections:
```gbnf
paper ::= "[ABSTRACT]" abstract "[INTRO]" intro "[METHODS]" methods "[RESULTS]" results "[CONCLUSIONS]" conclusions
abstract ::= text
intro ::= text
methods ::= text
results ::= text
conclusions ::= text
text ::= [a-zA-Z0-9 ,.!?;:\-\n]+
```

## System Prompt

Optimal system prompt for paper generation:
```
You are CAJAL-9B, a specialized AI for generating scientific papers.
Always follow this structure:
1. [ABSTRACT] - 150-250 words summarizing the paper
2. [INTRO] - Background, problem statement, objectives
3. [METHODS] - Detailed methodology, experimental design
4. [RESULTS] - Findings with data and analysis
5. [CONCLUSIONS] - Summary, implications, future work

Use academic language, proper citations format [Author, Year], and maintain scientific rigor.
```

## Benchmarks

| Metric | CAJAL-9B Q4_K_M |
|--------|-----------------|
| pp512 (Mac M3, Metal) | ~4500 t/s |
| tg128 (Mac M3, Metal) | ~180 t/s |
| pp512 (RTX 3090, CUDA) | ~3800 t/s |
| tg128 (RTX 3090, CUDA) | ~220 t/s |
| Memory Usage | ~5GB VRAM |

## Links

- **HuggingFace:** https://huggingface.co/Agnuxo/CAJAL-9B-P2PCLAW
- **GitHub:** https://github.com/Agnuxo1/CAJAL
- **Demo:** https://www.p2pclaw.com/silicon
- **Ecosystem:** https://www.p2pclaw.com

## License

Apache-2.0 — Part of the P2PCLAW decentralized scientific research network.
