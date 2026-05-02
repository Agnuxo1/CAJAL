# CAJAL + Zed Editor Integration

> Zed is a high-performance, multiplayer code editor.

## Setup

### 1. Configure Zed Assistant

Open Zed settings (~/.config/zed/settings.json):

`json
{
  "assistant": {
    "version": "2",
    "default_model": {
      "provider": "ollama",
      "model": "cajal-4b"
    },
    "default_width": 480,
    "providers": {
      "ollama": {
        "api_url": "http://localhost:11434",
        "low_speed_timeout_in_seconds": 120
      }
    }
  }
}
`

### 2. Using CAJAL in Zed

- **Open Assistant**: Ctrl+? (or Cmd+?)
- **Start chat**: Type your question and press Enter
- **Inline editing**: Select code → Right-click → "Generate" / "Transform"

### 3. CAJAL System Prompt

Add to Zed settings:

`json
{
  "assistant": {
    "inline_alternatives": [
      {
        "name": "CAJAL",
        "model": {
          "provider": "ollama",
          "model": "cajal-4b"
        }
      }
    ]
  }
}
`
"@

    "aider.md" = @"
# CAJAL + Aider Integration

> Aider is AI pair programming in your terminal.

## Setup

### 1. Install Aider

`ash
pip install aider-chat
`

### 2. Configure CAJAL Model

`ash
# Set environment variables
export OLLAMA_API_BASE=http://localhost:11434

# Run aider with CAJAL
aider --model ollama/cajal-4b
`

### 3. Using CAJAL with Aider

`ash
# Start with specific files
aider --model ollama/cajal-4b src/protocol.rs src/governance.rs

# Or use the CAJAL Bridge for OpenAI compatibility
export OPENAI_API_BASE=http://localhost:8765/v1
aider --model openai/cajal-4b
`

### 4. CAJAL-Powered Commands

Inside Aider chat:
- /add file.rs — Add files to context
- /commit — Let CAJAL write commit messages
- /test — Run tests after changes
- /architect — Discuss architecture before coding

## Tips

- CAJAL excels at reviewing consensus algorithm implementations
- Use /ask for questions without code changes
- Enable /auto-commits for rapid iteration
