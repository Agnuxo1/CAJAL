"""
CAJAL Jupyter Kernel Extension
Provides %%cajal magic command for generating papers in Jupyter notebooks.

Installation:
    pip install cajal-p2pclaw
    python -m cajal_p2pclaw.jupyter.install

Usage in notebook:
    %%cajal
    Topic: "Quantum machine learning"
    Format: full_paper
    References: 10
"""

from IPython.core.magic import register_cell_magic, register_line_magic
from IPython.display import Markdown, display
import requests
import json

# Global configuration
CAJAL_CONFIG = {
    "model": "cajal",
    "ollama_host": "http://localhost:11434",
    "temperature": 0.3,
    "max_tokens": 8192
}


def set_cajal_config(model=None, host=None, temperature=None):
    """Update CAJAL configuration."""
    if model:
        CAJAL_CONFIG["model"] = model
    if host:
        CAJAL_CONFIG["ollama_host"] = host
    if temperature is not None:
        CAJAL_CONFIG["temperature"] = temperature
    print(f"CAJAL config: {CAJAL_CONFIG}")


@register_cell_magic
def cajal(line, cell):
    """
    CAJAL magic command for Jupyter notebooks.
    
    Usage:
        %%cajal [command]
        Topic: "your research topic"
        Format: full_paper|abstract|methods|references
        References: 8
        
    Commands:
        paper      - Generate full paper (default)
        abstract   - Generate abstract only
        methods    - Generate methods section
        references - Find references
        review     - Review existing text
    """
    
    command = line.strip() or "paper"
    
    # Parse cell content
    params = {"topic": cell.strip(), "format": "full_paper", "references": 8}
    
    for line_text in cell.split('\n'):
        if ':' in line_text:
            key, value = line_text.split(':', 1)
            key = key.strip().lower()
            value = value.strip().strip('"').strip("'")
            if key in ["topic", "format", "references", "style", "venue"]:
                params[key] = value if key != "references" else int(value)
    
    # Build prompt based on command
    prompts = {
        "paper": f"Generate a complete scientific paper on: {params['topic']}. Include Abstract, Introduction, Related Work, Methodology, Results, Discussion, Conclusion, and {params['references']} references.",
        "abstract": f"Write an academic abstract (150-250 words) for: {params['topic']}. Include background, methods, key results, and conclusion.",
        "methods": f"Write a detailed, reproducible methodology section for research on: {params['topic']}. Include materials, procedures, parameters, datasets, and evaluation metrics.",
        "references": f"Suggest {params['references']} relevant academic references for: {params['topic']}. Include author, year, title, venue, and DOI/arXiv ID.",
        "review": f"Review the following text and suggest improvements for scientific writing quality: {params['topic']}"
    }
    
    prompt = prompts.get(command, prompts["paper"])
    
    # Call Ollama
    try:
        response = requests.post(
            f"{CAJAL_CONFIG['ollama_host']}/api/generate",
            json={
                "model": CAJAL_CONFIG["model"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": CAJAL_CONFIG["temperature"],
                    "num_ctx": 32768,
                    "top_p": 0.9
                }
            },
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json().get("response", "")
            
            # Display as markdown
            display(Markdown(result))
            
            # Also store in a variable for further use
            get_ipython().user_ns['_cajal_last_output'] = result
            print(f"\n[Stored in _cajal_last_output variable]")
        else:
            print(f"Error: Ollama returned {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")


@register_line_magic
def cajal_config(line):
    """Configure CAJAL settings."""
    args = line.split()
    if len(args) >= 2:
        key, value = args[0], args[1]
        if key == "model":
            CAJAL_CONFIG["model"] = value
        elif key == "host":
            CAJAL_CONFIG["ollama_host"] = value
        elif key == "temperature":
            CAJAL_CONFIG["temperature"] = float(value)
        print(f"Updated {key} = {value}")
    else:
        print("Usage: %cajal_config model <name> | host <url> | temperature <value>")
        print(f"Current: {CAJAL_CONFIG}")


# Auto-load on import
print("✅ CAJAL Jupyter extension loaded!")
print("   Magic commands: %%cajal, %cajal_config")
print(f"   Default model: {CAJAL_CONFIG['model']} @ {CAJAL_CONFIG['ollama_host']}")
