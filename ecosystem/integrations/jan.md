# CAJAL + Jan Integration

> Jan is a ChatGPT-alternative that runs 100% offline.

## Setup

### 1. Download Jan

Get it from [jan.ai](https://jan.ai)

### 2. Import CAJAL-4B

1. Open Jan
2. Go to **Settings → Models**
3. Click **Import Model**
4. Select your CAJAL-4B-f16.gguf file
5. Set parameters:
   - **Context Length**: 4096
   - **Temperature**: 0.7
   - **Top P**: 0.9

### 3. Configure System Prompt

In the model settings, set:

`
You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich...
`

### 4. Start Chatting

Create a new thread and select CAJAL-4B from the model dropdown.

## Advanced Features

- **Thread history**: All conversations saved locally
- **Model management**: Easy switching between models
- **Extensions**: Add RAG and other capabilities
- **API server**: Built-in local API for other tools
