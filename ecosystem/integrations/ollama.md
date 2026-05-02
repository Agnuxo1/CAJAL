# CAJAL + Ollama Integration

> Primary backend for all CAJAL deployments.

## Prerequisites

- [Ollama](https://ollama.com) installed
- CAJAL-4B GGUF file or Modelfile

## Quick Install

If you used the CAJAL installer, Ollama and the model are already configured.

### Manual Setup

```bash
# Create the model in Ollama
ollama create cajal-4b -f /path/to/Modelfile

# Verify installation
ollama list

# Run interactive chat
ollama run cajal-4b
```

## Modelfile Reference

```dockerfile
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

SYSTEM """You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich..."""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER stop <|im_end|>
```

## API Usage

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "cajal-4b",
  "messages": [{"role":"user","content":"Explain P2PCLAW governance"}]
}'
```

## Integration Status

| Feature | Status |
|---------|--------|
| Local inference | ✅ Native |
| OpenAI-compatible API | ✅ via CAJAL Bridge |
| Multi-turn chat | ✅ |
| System prompts | ✅ |

## Troubleshooting

- **Model not found**: Run `ollama create cajal-4b -f Modelfile`
- **Out of memory**: Use `PARAMETER num_ctx 2048` or quantize to Q4_K_M
- **Slow responses**: Ensure GPU is being used (check `ollama ps`)
