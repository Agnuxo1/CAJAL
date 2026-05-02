# LM Studio Plugin for CAJAL-4B

## Overview

[LM Studio](https://lmstudio.ai) supports custom tools via TypeScript plugins. This guide creates a CAJAL-4B tool provider.

## Plugin Structure

Create `~/.lmstudio/plugins/cajal/`:

```typescript
// index.ts
import { LMStudioClient } from "@lmstudio/sdk";

const client = new LMStudioClient();

export const cajalPlugin = {
  name: "cajal",
  version: "1.0.0",
  description: "P2PCLAW AI Assistant integration",
  
  async load() {
    const model = await client.llm.load("cajal-4b", {
      config: {
        contextLength: 4096,
        temperature: 0.7
      }
    });
    
    return {
      tools: [
        {
          name: "p2pclaw_research",
          description: "Research P2PCLAW protocols",
          parameters: {
            query: { type: "string", description: "Research query" }
          },
          async execute({ query }) {
            const prediction = model.respond([
              { role: "system", content: "You are CAJAL, P2PCLAW researcher." },
              { role: "user", content: `Research: ${query}` }
            ]);
            return await prediction;
          }
        },
        {
          name: "code_audit",
          description: "Audit code for P2PCLAW compliance",
          parameters: {
            code: { type: "string", description: "Code to audit" }
          },
          async execute({ code }) {
            const prediction = model.respond([
              { role: "system", content: "You are CAJAL, security auditor." },
              { role: "user", content: `Audit this code:\n\`\`\`\n${code}\n\`\`\`` }
            ]);
            return await prediction;
          }
        }
      ]
    };
  }
};
```

## manifest.json

```json
{
  "name": "cajal-lmstudio",
  "version": "1.0.0",
  "description": "CAJAL-4B P2PCLAW Assistant",
  "author": "P2PCLAW",
  "main": "index.ts",
  "lmstudio": {
    "minVersion": "0.3.0",
    "capabilities": ["tools", "chat"]
  }
}
```

## Installation

1. Open LM Studio → Plugins
2. Click "Install from Folder"
3. Select `~/.lmstudio/plugins/cajal/`
4. Restart LM Studio

## Usage

1. Load CAJAL-4B model in LM Studio
2. In chat, use `@cajal` to access tools
3. Or use the tool buttons in the UI

## Links

- LM Studio: https://lmstudio.ai
- LM Studio Plugins: https://lmstudio.ai/docs/typescript/plugins
- CAJAL: https://github.com/Agnuxo1/CAJAL
