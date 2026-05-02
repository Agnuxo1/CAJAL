export interface CajalConfig {
  serverUrl?: string;
  model?: string;
  maxTokens?: number;
  temperature?: number;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  response: string;
  model: string;
  tokens_used?: number;
}

export class CAJALClient {
  private serverUrl: string;
  private model: string;
  private maxTokens: number;
  private temperature: number;

  constructor(config: CajalConfig = {}) {
    this.serverUrl = config.serverUrl || 'http://localhost:8000';
    this.model = config.model || 'Agnuxo/CAJAL-4B-P2PCLAW';
    this.maxTokens = config.maxTokens || 512;
    this.temperature = config.temperature || 0.7;
  }

  /**
   * Send a single message to CAJAL
   */
  async chat(message: string): Promise<string> {
    const res = await fetch(`${this.serverUrl}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [{ role: 'user', content: message }],
        model: this.model,
        max_new_tokens: this.maxTokens,
        temperature: this.temperature
      })
    });

    if (!res.ok) {
      throw new Error(`CAJAL error: ${res.status} ${res.statusText}`);
    }

    const data = await res.json() as ChatResponse;
    return data.response;
  }

  /**
   * Multi-turn conversation
   */
  async sendMessages(messages: ChatMessage[]): Promise<string> {
    const res = await fetch(`${this.serverUrl}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages,
        model: this.model,
        max_new_tokens: this.maxTokens,
        temperature: this.temperature
      })
    });

    if (!res.ok) {
      throw new Error(`CAJAL error: ${res.status} ${res.statusText}`);
    }

    const data = await res.json() as ChatResponse;
    return data.response;
  }

  /**
   * Stream response (if server supports it)
   */
  async *stream(message: string): AsyncGenerator<string, void, unknown> {
    const res = await fetch(`${this.serverUrl}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [{ role: 'user', content: message }],
        model: this.model,
        max_new_tokens: this.maxTokens,
        temperature: this.temperature,
        stream: true
      })
    });

    const reader = res.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      yield decoder.decode(value, { stream: true });
    }
  }
}

// Default export for easy import
export default CAJALClient;
