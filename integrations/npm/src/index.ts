/**
 * CAJAL JavaScript/TypeScript SDK
 * Scientific Paper Generator for Node.js and browsers
 * 
 * @example
 * ```typescript
 * import { CAJAL } from 'cajal-p2pclaw';
 * 
 * const cajal = new CAJAL({ model: 'cajal' });
 * const paper = await cajal.generatePaper('Quantum error correction');
 * console.log(paper);
 * ```
 */

export interface CAJALConfig {
  /** Ollama model name (default: 'cajal') */
  model?: string;
  /** Ollama host URL (default: 'http://localhost:11434') */
  host?: string;
  /** Generation temperature (default: 0.3) */
  temperature?: number;
  /** Max tokens (default: 8192) */
  maxTokens?: number;
  /** Context window (default: 32768) */
  contextWindow?: number;
}

export interface PaperOptions {
  /** Paper topic */
  topic: string;
  /** Output format */
  format?: 'markdown' | 'latex' | 'abstract' | 'methods' | 'references';
  /** Minimum references (default: 8) */
  minReferences?: number;
  /** Paper style */
  style?: 'academic' | 'technical' | 'review';
}

export class CAJAL {
  private config: Required<CAJALConfig>;

  constructor(config: CAJALConfig = {}) {
    this.config = {
      model: config.model || 'cajal',
      host: config.host || 'http://localhost:11434',
      temperature: config.temperature ?? 0.3,
      maxTokens: config.maxTokens ?? 8192,
      contextWindow: config.contextWindow ?? 32768
    };
  }

  /**
   * Generate a complete scientific paper
   */
  async generatePaper(options: PaperOptions): Promise<string> {
    const prompt = this.buildPrompt(options);
    return this.callOllama(prompt);
  }

  /**
   * Generate an abstract (150-250 words)
   */
  async generateAbstract(topic: string): Promise<string> {
    return this.generatePaper({
      topic,
      format: 'abstract'
    });
  }

  /**
   * Generate a methodology section
   */
  async generateMethods(topic: string): Promise<string> {
    return this.generatePaper({
      topic,
      format: 'methods'
    });
  }

  /**
   * Find relevant references
   */
  async findReferences(topic: string, count: number = 10): Promise<string[]> {
    const result = await this.generatePaper({
      topic,
      format: 'references',
      minReferences: count
    });
    return result.split('\n').filter(line => line.trim().length > 0);
  }

  /**
   * Check if Ollama is available
   */
  async checkStatus(): Promise<{ ok: boolean; model: string; error?: string }> {
    try {
      const response = await fetch(`${this.config.host}/api/tags`);
      if (!response.ok) {
        return { ok: false, model: this.config.model, error: `HTTP ${response.status}` };
      }
      const data = await response.json();
      const hasModel = data.models?.some((m: any) => m.name.includes(this.config.model));
      return { ok: hasModel, model: this.config.model, error: hasModel ? undefined : 'Model not found' };
    } catch (error) {
      return { ok: false, model: this.config.model, error: String(error) };
    }
  }

  private buildPrompt(options: PaperOptions): string {
    const system = `You are CAJAL (Cognitive Academic Journal Authoring Layer), a specialized scientific paper authoring assistant.

Generate publication-ready scientific papers with:
- Formal academic tone
- Proper structure (Abstract → Introduction → Methods → Results → Discussion → Conclusion → References)
- Real citations where possible
- Reproducible methodology
- Quantitative, evidence-based claims`;

    const formatPrompts: Record<string, string> = {
      markdown: `Generate a complete scientific paper in markdown format on: ${options.topic}. Include Abstract, Introduction, Related Work, Methodology, Results, Discussion, Conclusion, and ${options.minReferences || 8} references.`,
      latex: `Generate a complete scientific paper in LaTeX format on: ${options.topic}. Include all standard sections and ${options.minReferences || 8} references.`,
      abstract: `Write an academic abstract (150-250 words) for a paper on: ${options.topic}. Include background, methods, key results, and conclusion.`,
      methods: `Write a detailed, reproducible methodology section for research on: ${options.topic}. Include materials, procedures, parameters, datasets, and evaluation metrics.`,
      references: `Suggest ${options.minReferences || 10} relevant academic references for: ${options.topic}. Include author, year, title, venue, and DOI/arXiv ID.`
    };

    return `${system}\n\n${formatPrompts[options.format || 'markdown']}`;
  }

  private async callOllama(prompt: string): Promise<string> {
    const response = await fetch(`${this.config.host}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: this.config.model,
        prompt,
        stream: false,
        options: {
          temperature: this.config.temperature,
          num_predict: this.config.maxTokens,
          num_ctx: this.config.contextWindow,
          top_p: 0.9,
          repeat_penalty: 1.1
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Ollama error: ${response.status}`);
    }

    const data = await response.json();
    return data.response;
  }
}

export default CAJAL;