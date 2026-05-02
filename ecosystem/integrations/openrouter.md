# CAJAL + OpenRouter / LiteLLM Integration

> Use CAJAL as a unified API endpoint for multiple applications.

## LiteLLM Setup

### 1. Install LiteLLM

`ash
pip install litellm
`

### 2. Configure CAJAL (Ollama Backend)

Create litellm_config.yaml:

`yaml
model_list:
  - model_name: cajal-4b
    litellm_params:
      model: ollama/cajal-4b
      api_base: http://localhost:11434

  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-3
    litellm_params:
      model: anthropic/claude-3-opus
      api_key: os.environ/ANTHROPIC_API_KEY

general_settings:
  master_key: sk-cajal-master-key
`

### 3. Start LiteLLM Proxy

`ash
litellm --config litellm_config.yaml --port 8000
`

### 4. Use CAJAL via OpenAI-Compatible API

`ash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-cajal-master-key" \
  -d '{
    "model": "cajal-4b",
    "messages": [{"role":"user","content":"Explain P2PCLAW"}]
  }'
`

## Connecting Applications

Any tool that supports OpenAI API can now use CAJAL through LiteLLM:

| Tool | Endpoint | Model Name |
|------|----------|------------|
| OpenCode | http://localhost:8000/v1 | cajal-4b |
| Continue.dev | http://localhost:8000/v1 | cajal-4b |
| Cursor | http://localhost:8000/v1 | cajal-4b |
| Custom apps | http://localhost:8000/v1 | cajal-4b |

## Benefits

- 🔑 Single API key for all models
- 📊 Usage tracking and rate limiting
- 💰 Cost optimization (fallback models)
- 🔒 Request/response logging
