# CAJAL + AnythingLLM Integration

> AnythingLLM is a private ChatGPT alternative with RAG capabilities.

## Setup

### 1. Install AnythingLLM

Download from [anythingllm.com](https://anythingllm.com)

### 2. Configure Ollama Backend

1. Launch AnythingLLM
2. **Select LLM Provider** → Choose **Ollama**
3. **Ollama Base URL**: http://host.docker.internal:114114 (or http://127.0.0.1:11434)
4. **Model Preference**: Select cajal-4b

### 3. Create P2PCLAW Workspace

1. **New Workspace** → Name: "P2PCLAW Research"
2. **System Prompt**:
`
You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland...
`
3. **Temperature**: 0.7

### 4. Upload Documents

Upload P2PCLAW papers, protocol specifications, and research:
- PDF research papers
- Markdown protocol docs
- Code repositories

### 5. Chat with CAJAL + Your Documents

CAJAL will reference uploaded documents when answering questions about P2PCLAW protocols.

## Use Cases

- **Research Q&A**: Ask questions about uploaded papers
- **Protocol comparison**: Compare different governance mechanisms
- **Citation**: Get exact references from documents
