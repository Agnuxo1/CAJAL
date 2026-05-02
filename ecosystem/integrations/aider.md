# CAJAL + Aider Integration

> Aider is AI pair programming in your terminal.

## Setup

### 1. Install Aider

```bash
pip install aider-chat
```

### 2. Configure CAJAL Model

```bash
# Set environment variables
export OLLAMA_API_BASE=http://localhost:11434

# Run aider with CAJAL
aider --model ollama/cajal-4b
```

### 3. Using CAJAL with Aider

```bash
# Start with specific files
aider --model ollama/cajal-4b src/protocol.rs src/governance.rs

# Or use the CAJAL Bridge for OpenAI compatibility
export OPENAI_API_BASE=http://localhost:8765/v1
aider --model openai/cajal-4b
```

### 4. CAJAL-Powered Commands

Inside Aider chat:
- `/add file.rs` — Add files to context
- `/commit` — Let CAJAL write commit messages
- `/test` — Run tests after changes
- `/architect` — Discuss architecture before coding

## Tips

- CAJAL excels at reviewing consensus algorithm implementations
- Use `/ask` for questions without code changes
- Enable `/auto-commits` for rapid iteration
