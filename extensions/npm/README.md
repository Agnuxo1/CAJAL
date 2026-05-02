# CAJAL-4B-P2PCLAW JavaScript SDK

🧠 **Scientific intelligence for decentralized research networks**

```bash
npm install cajal-p2pclaw
```

## Quick Start

```typescript
import { CAJALClient } from 'cajal-p2pclaw';

const cajal = new CAJALClient({
  serverUrl: 'http://localhost:8000',  // Your cajal-server
  model: 'Agnuxo/CAJAL-4B-P2PCLAW'
});

const response = await cajal.chat(
  "Explain zero-knowledge proofs in P2P networks."
);
console.log(response);
```

## Multi-turn Conversation

```typescript
const messages = [
  { role: 'system', content: 'You are a research assistant.' },
  { role: 'user', content: 'What is Byzantine consensus?' },
  { role: 'assistant', content: 'Byzantine consensus is...' },
  { role: 'user', content: 'How does it apply to P2P?' }
];

const response = await cajal.sendMessages(messages);
```

## Streaming

```typescript
for await (const chunk of cajal.stream("Explain post-quantum crypto.")) {
  process.stdout.write(chunk);
}
```

## Prerequisites

- Running `cajal-server` (install: `pip install cajal-p2pclaw && cajal-server --port 8000`)
- Or any OpenAI-compatible endpoint

## Links

- [Python Package](https://pypi.org/project/cajal-p2pclaw/)
- [HuggingFace Model](https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW)
- [GitHub](https://github.com/Agnuxo1/CAJAL)

**MIT License** — Francisco Angulo de Lafuente (Agnuxo1)
