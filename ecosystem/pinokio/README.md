# Pinokio Launcher for CAJAL-4B

## Overview

[Pinokio](https://pinokio.co) is a browser-based AI application launcher. This JSON configuration enables one-click installation of CAJAL-4B.

## Installation

1. Install [Pinokio](https://pinokio.co)
2. Click "Install from GitHub"
3. Enter: `https://github.com/Agnuxo1/CAJAL`
4. Or download `pinokio.json` and drag it into Pinokio

## Manual Setup

Place `pinokio.json` in your Pinokio scripts directory:

```bash
# macOS
~/Library/Application Support/pinokio/scripts/cajal/

# Windows
%APPDATA%\pinokio\scripts\cajal\

# Linux
~/.config/pinokio/scripts/cajal/
```

## What It Does

1. Installs the `cajal` Python package via pip
2. Downloads CAJAL-4B from HuggingFace (if needed)
3. Starts the OpenAI-compatible API server on port 8765
4. Provides health check endpoint

## Access

Once running, access CAJAL at:
- **API**: http://localhost:8765/v1/chat/completions
- **Health**: http://localhost:8765/health
- **Models**: http://localhost:8765/v1/models

## Links

- Pinokio: https://pinokio.co
- CAJAL: https://github.com/Agnuxo1/CAJAL
- HuggingFace: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW
