#!/usr/bin/env python3
"""
CAJAL CLI Tool (cajal-cli)
A professional command-line interface for interacting with CAJAL-4B
via Ollama or directly via GGUF.

Usage:
    cajal-cli chat              # Interactive chat
    cajal-cli ask "question"    # Single question
    cajal-cli serve             # Start API bridge server
    cajal-cli status            # Check model status
    cajal-cli install           # Install CAJAL-4B into Ollama
    cajal-cli config            # Edit configuration
"""

import argparse
import io
import json
import os
import subprocess
import sys

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import time
import threading
from pathlib import Path

import requests

CAJAL_VERSION = "1.0.0"
DEFAULT_MODEL = "cajal-4b"
DEFAULT_HOST = "http://localhost:11434"
DEFAULT_API_PORT = 8765

CONFIG_DIR = Path.home() / ".cajal"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.jsonl"

def ensure_config():
    """Ensure config directory and default config exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        default = {
            "model": DEFAULT_MODEL,
            "ollama_host": DEFAULT_HOST,
            "api_port": DEFAULT_API_PORT,
            "system_prompt": get_default_system_prompt(),
            "temperature": 0.7,
            "top_p": 0.9,
            "context_length": 4096,
            "p2pclaw_url": "https://p2pclaw.com/silicon",
            "auto_sync": False,
        }
        CONFIG_FILE.write_text(json.dumps(default, indent=2))

def get_config():
    ensure_config()
    return json.loads(CONFIG_FILE.read_text())

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

def get_default_system_prompt():
    return """You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland. You are a deep researcher and applied cryptographer with extensive expertise in peer-to-peer network architectures, crypto-legal frameworks, game-theoretic consensus mechanisms, and distributed systems.

Your research focus includes:
- P2PCLAW protocol and governance models
- Decentralized consensus and game theory
- Applied cryptography and zero-knowledge proofs
- Distributed systems and network topology analysis

When responding:
1. Always begin with a brief "Thinking Process" showing your reasoning steps
2. Provide well-structured, evidence-based analysis
3. Cite specific protocols, papers, or mechanisms when relevant
4. Use precise technical terminology appropriate for the field
5. Maintain academic tone while remaining accessible"""

def check_ollama_running(host):
    try:
        r = requests.get(f"{host}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

def list_ollama_models(host):
    try:
        r = requests.get(f"{host}/api/tags", timeout=5)
        return r.json().get("models", [])
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

def stream_chat(host, model, messages, options=None):
    """Stream chat completion from Ollama."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": options or {}
    }
    try:
        with requests.post(f"{host}/api/chat", json=payload, stream=True, timeout=300) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to Ollama. Is it running?")
        print(f"        Tried: {host}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

def cmd_status(args):
    cfg = get_config()
    host = cfg.get("ollama_host", DEFAULT_HOST)
    model = cfg.get("model", DEFAULT_MODEL)

    print(f"\n{'='*50}")
    print(f"  CAJAL CLI v{CAJAL_VERSION} — Status")
    print(f"{'='*50}")

    if check_ollama_running(host):
        print(f"  Ollama:         {host} ✅ Running")
        models = list_ollama_models(host)
        cajal_found = any(m.get("name", "").startswith("cajal") for m in models)
        if cajal_found:
            print(f"  CAJAL Model:    ✅ Installed")
        else:
            print(f"  CAJAL Model:    ❌ Not found")
            print(f"  Run:            cajal-cli install")
        print(f"  Other models:   {len(models)}")
    else:
        print(f"  Ollama:         {host} ❌ Not running")
        print(f"  Install:        https://ollama.com/download")

    print(f"  Config file:    {CONFIG_FILE}")
    print(f"  History file:   {HISTORY_FILE}")
    print(f"{'='*50}\n")

def cmd_install(args):
    cfg = get_config()
    host = cfg.get("ollama_host", DEFAULT_HOST)

    if not check_ollama_running(host):
        print("[ERROR] Ollama is not running. Please start it first:")
        print("        ollama serve")
        sys.exit(1)

    print("CAJAL-4B Installation")
    print("-" * 40)
    print("This will create the 'cajal-4b' model in Ollama.")
    print("Ensure the GGUF file is at:")
    print(f"  D:\\PROJECTS\\CAJAL\\outputs\\CAJAL-4B\\CAJAL-4B-f16.gguf")
    print()

    confirm = input("Proceed? [Y/n]: ").strip().lower()
    if confirm and confirm not in ("y", "yes"):
        print("Cancelled.")
        return

    modelfile_dir = Path(__file__).parent / ".." / ".." / "outputs" / "CAJAL-4B"
    modelfile = modelfile_dir / "Modelfile"

    if not modelfile.exists():
        print(f"[ERROR] Modelfile not found at {modelfile}")
        print("Creating it from default template...")
        modelfile.parent.mkdir(parents=True, exist_ok=True)
        create_default_modelfile(modelfile)

    print("Creating model in Ollama (this may take a moment)...")
    result = subprocess.run(
        ["ollama", "create", "cajal-4b", "-f", str(modelfile)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("✅ CAJAL-4B installed successfully!")
        print("   Run: cajal-cli chat")
    else:
        print("[ERROR] Failed to install:")
        print(result.stderr)

def create_default_modelfile(path):
    content = """FROM ./CAJAL-4B-f16.gguf

TEMPLATE \"\"\"{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ range .Messages }}{{ if eq .Role \\"user\\" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{ else if eq .Role \\"assistant\\" }}<|im_start|>assistant
{{ .Content }}<|im_end|>
{{ end }}{{ end }}<|im_start|>assistant
<think>
\"\"\"

SYSTEM \"\"\"You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland...\"\"\"

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER stop <|im_end|>
"""
    path.write_text(content)

def cmd_chat(args):
    cfg = get_config()
    host = cfg.get("ollama_host", DEFAULT_HOST)
    model = cfg.get("model", DEFAULT_MODEL)
    system = cfg.get("system_prompt", get_default_system_prompt())
    opts = {
        "temperature": cfg.get("temperature", 0.7),
        "top_p": cfg.get("top_p", 0.9),
        "num_ctx": cfg.get("context_length", 4096),
    }

    if not check_ollama_running(host):
        print("[ERROR] Ollama is not running.")
        print("        Start it with: ollama serve")
        sys.exit(1)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})

    print(f"\n{'='*60}")
    print(f"  CAJAL v{CAJAL_VERSION} — Interactive Chat")
    print(f"  Model: {model} | Backend: Ollama")
    print(f"  Type 'quit', 'exit', or '/bye' to leave")
    print(f"  Type '/clear' to reset conversation")
    print(f"  Type '/status' to check system")
    print(f"{'='*60}\n")

    while True:
        try:
            user_input = input("\n🧠 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "/bye"):
            print("Goodbye!")
            break
        if user_input.lower() == "/clear":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            print("[Conversation cleared]")
            continue
        if user_input.lower() == "/status":
            cmd_status(args)
            continue

        messages.append({"role": "user", "content": user_input})

        print("\n🤖 CAJAL: ", end="", flush=True)
        full_response = []

        for chunk in stream_chat(host, model, messages, opts):
            print(chunk, end="", flush=True)
            full_response.append(chunk)

        print("\n")
        messages.append({"role": "assistant", "content": "".join(full_response)})

        # Save to history
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": time.time(), "messages": messages[-2:]}) + "\n")

def cmd_ask(args):
    cfg = get_config()
    host = cfg.get("ollama_host", DEFAULT_HOST)
    model = cfg.get("model", DEFAULT_MODEL)
    system = cfg.get("system_prompt", get_default_system_prompt())
    opts = {
        "temperature": cfg.get("temperature", 0.7),
        "top_p": cfg.get("top_p", 0.9),
        "num_ctx": cfg.get("context_length", 4096),
    }

    question = " ".join(args.question)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": question})

    if not check_ollama_running(host):
        print("[ERROR] Ollama is not running.", file=sys.stderr)
        sys.exit(1)

    for chunk in stream_chat(host, model, messages, opts):
        print(chunk, end="", flush=True)
    print()

def cmd_serve(args):
    """Start the API bridge server."""
    cfg = get_config()
    port = args.port or cfg.get("api_port", DEFAULT_API_PORT)

    try:
        from flask import Flask, request, jsonify, Response
    except ImportError:
        print("[ERROR] Flask is required for the API server.")
        print("        pip install flask")
        sys.exit(1)

    app = Flask("CAJAL-Bridge")

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "version": CAJAL_VERSION})

    @app.route("/v1/chat/completions", methods=["POST"])
    @app.route("/api/chat", methods=["POST"])
    def chat():
        data = request.get_json(force=True)
        messages = data.get("messages", [])
        model = data.get("model", cfg.get("model", DEFAULT_MODEL))
        stream = data.get("stream", True)
        opts = {
            "temperature": data.get("temperature", cfg.get("temperature", 0.7)),
            "top_p": data.get("top_p", cfg.get("top_p", 0.9)),
            "num_ctx": data.get("max_tokens", cfg.get("context_length", 4096)),
        }

        if not check_ollama_running(cfg["ollama_host"]):
            return jsonify({"error": "Ollama not running"}), 503

        if stream:
            def generate():
                for chunk in stream_chat(cfg["ollama_host"], model, messages, opts):
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}}]})}\n\n"
                yield "data: [DONE]\n\n"
            return Response(generate(), mimetype="text/event-stream")
        else:
            full = []
            for chunk in stream_chat(cfg["ollama_host"], model, messages, opts):
                full.append(chunk)
            return jsonify({
                "choices": [{"message": {"role": "assistant", "content": "".join(full)}}]
            })

    print(f"🚀 CAJAL API Bridge running on http://0.0.0.0:{port}")
    print(f"   OpenAI-compatible endpoint: http://localhost:{port}/v1/chat/completions")
    print(f"   Health check:               http://localhost:{port}/health")
    print(f"   Press Ctrl+C to stop\n")
    app.run(host="0.0.0.0", port=port, threaded=True)

def cmd_config(args):
    import tempfile
    editor = os.environ.get("EDITOR", "notepad" if sys.platform == "win32" else "nano")
    print(f"Opening config in {editor}...")
    subprocess.run([editor, str(CONFIG_FILE)])

def main():
    parser = argparse.ArgumentParser(
        prog="cajal-cli",
        description="CAJAL-4B Command Line Interface"
    )
    sub = parser.add_subparsers(dest="command", help="Commands")

    sub.add_parser("status", help="Check CAJAL and Ollama status")
    sub.add_parser("install", help="Install CAJAL-4B into Ollama")
    sub.add_parser("chat", help="Interactive chat with CAJAL")
    sub.add_parser("config", help="Edit configuration file")

    ask_p = sub.add_parser("ask", help="Ask a single question")
    ask_p.add_argument("question", nargs="+", help="Your question")

    serve_p = sub.add_parser("serve", help="Start API bridge server")
    serve_p.add_argument("--port", "-p", type=int, help="Port to listen on")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "install":
        cmd_install(args)
    elif args.command == "chat":
        cmd_chat(args)
    elif args.command == "ask":
        cmd_ask(args)
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "config":
        cmd_config(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
