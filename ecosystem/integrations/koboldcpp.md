# CAJAL + KoboldCPP Integration

> KoboldCPP is a retro-inspired, user-friendly AI text generation interface.

## Setup

### 1. Download KoboldCPP

Get the latest release from [github.com/LostRuins/koboldcpp](https://github.com/LostRuins/koboldcpp)

### 2. Launch with CAJAL-4B

```bash
# Windows
koboldcpp.exe --model CAJAL-4B-f16.gguf --port 5001 --contextsize 4096

# Linux/macOS
./koboldcpp --model CAJAL-4B-f16.gguf --port 5001 --contextsize 4096
```

### 3. Configure Character

1. Open the web UI at `http://localhost:5001`
2. Go to **Settings → AI**
3. Set **System Prompt**:
```
You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich, Switzerland...
```

### 4. Using CAJAL in KoboldCPP

- **Story Mode**: Write research narratives with CAJAL
- **Adventure Mode**: Interactive technical exploration
- **Chat Mode**: Direct Q&A with CAJAL
- **Instruct Mode**: Following precise technical instructions

## Features

- **Memory**: CAJAL remembers context across sessions
- **World Info**: Create P2PCLAW lore database
- **Author's Note**: Inject research context
- **Token streaming**: Real-time CAJAL responses

## API Access

KoboldCPP exposes an API at `http://localhost:5001/api/v1/generate` for integration with other tools.
