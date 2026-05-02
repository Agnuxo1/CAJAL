# CAJAL + Text Generation WebUI Integration

> text-generation-webui (oobabooga) is a Gradio web UI for running LLMs.

## Setup

### 1. Install text-generation-webui

```bash
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui
./start_linux.sh
```

### 2. Load CAJAL-4B

1. Place `CAJAL-4B-f16.gguf` in the `models/` folder
2. Launch the UI
3. Go to **Model** tab
4. Select `CAJAL-4B-f16.gguf` from the dropdown
5. Set **n_ctx**: 4096
6. Click **Load**

### 3. Configure Character

Go to **Parameters → Character** and set:

```
Name: CAJAL
Context: You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich, Switzerland...
```

### 4. API Mode

Enable the API for external tools:

```bash
python server.py --api --listen --model CAJAL-4B-f16.gguf
```

API endpoint: `http://localhost:5000/v1/chat/completions`

## Advanced Features

- **Extensions**: Use the `superbooga` extension for document RAG
- **Multimodal**: Supports vision if using multimodal base
- **Presets**: Save CAJAL generation presets
