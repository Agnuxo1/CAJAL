#!/usr/bin/env python3
"""
CAJAL CLI Tool (cajal-cli)
A professional command-line interface for interacting with CAJAL-4B
via Ollama or directly via the HuggingFace model.

Usage:
    cajal chat              # Interactive chat
    cajal ask "question"    # Single question
    cajal serve             # Start API bridge server
    cajal status            # Check model status
    cajal install           # Install CAJAL-4B into Ollama
    cajal config            # Edit configuration
    cajal list              # List available models
    cajal webapp            # Launch web chat UI
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

# Fix UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import requests

from .config import get_config, save_config, DEFAULT_CONFIG

CAJAL_VERSION = "1.0.0"
DEFAULT_MODEL = "cajal-4b"
MODEL_REPO = "Agnuxo/CAJAL-4B-P2PCLAW"
DEFAULT_HOST = "http://localhost:11434"
DEFAULT_API_PORT = 8765


def get_config_dir() -> Path:
    """Return the configuration directory."""
    config_dir = Path.home() / ".cajal"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_history_file() -> Path:
    """Return the history file path."""
    return get_config_dir() / "history.jsonl"


def check_ollama_running(host: str) -> bool:
    """Check if Ollama server is running."""
    try:
        r = requests.get(f"{host}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def list_ollama_models(host: str) -> list:
    """List available Ollama models."""
    try:
        r = requests.get(f"{host}/api/tags", timeout=5)
        return r.json().get("models", [])
    except Exception as e:
        print(f"Error listing models: {e}")
        return []


def stream_chat(
    host: str, model: str, messages: list, options: Optional[dict] = None
) -> str:
    """Stream chat completion from Ollama."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": options or {},
    }
    try:
        with requests.post(
            f"{host}/api/chat", json=payload, stream=True, timeout=300
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to Ollama. Is it running?")
        print(f"        Tried: {host}")
        print("\nTo start Ollama:")
        print("    ollama serve")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


def cmd_status(args: argparse.Namespace) -> None:
    """Show CAJAL and Ollama status."""
    cfg = get_config()
    host = cfg.get("ollama_host", DEFAULT_HOST)
    model = cfg.get("model", DEFAULT_MODEL)

    print(f"\n{'='*56}")
    print(f"  CAJAL CLI v{CAJAL_VERSION} - Status")
    print(f"{'='*56}")
    print(f"  Model: {model}")
    print(f"  HF Repo: {MODEL_REPO}")
    print(f"  P2PCLAW: https://p2pclaw.com/silicon")
    print(f"{'='*56}")

    if check_ollama_running(host):
        print(f"  Ollama: {host} [OK]")
        models = list_ollama_models(host)
        cajal_found = any(m.get("name", "").startswith("cajal") for m in models)
        if cajal_found:
            print(f"  CAJAL Model: [OK] Installed")
        else:
            print(f"  CAJAL Model: [NOT FOUND]")
            print(f"  Install: cajal install")
        print(f"  Models available: {len(models)}")
        for m in models:
            name = m.get("name", "unknown")
            size = m.get("size", 0)
            size_gb = size / (1024**3) if size else 0
            print(f"    - {name} ({size_gb:.1f} GB)")
    else:
        print(f"  Ollama: {host} [OFFLINE]")
        print(f"  Install: https://ollama.com/download")
        print(f"  Then run: ollama serve")

    print(f"{'='*56}")
    print(f"  Config: {get_config_dir() / 'config.json'}")
    print(f"  History: {get_history_file()}")
    print(f"{'='*56}\n")


def cmd_install(args: argparse.Namespace) -> None:
    """Install CAJAL-4B into Ollama."""
    cfg = get_config()
    host = cfg.get("ollama_host", DEFAULT_HOST)

    if not check_ollama_running(host):
        print("[ERROR] Ollama is not running. Please start it first:")
        print("        ollama serve")
        sys.exit(1)

    print("="*56)
    print("  CAJAL-4B Installation")
    print("="*56)
    print()
    print("This will create the 'cajal-4b' model in Ollama.")
    print(f"Source: {MODEL_REPO}")
    print()

    method = input("Install from [1] HuggingFace or [2] local GGUF? [1]: ").strip() or "1"

    if method == "1":
        print("\nPulling CAJAL-4B from HuggingFace via Ollama...")
        print("This may take several minutes (model is ~8 GB).\n")

        result = subprocess.run(
            ["ollama", "pull", MODEL_REPO],
            capture_output=False,
            text=True,
        )
        if result.returncode == 0:
            print("\n[OK] CAJAL-4B installed successfully!")
            print("   Run: cajal chat")
        else:
            print("\n[ERROR] Failed to pull model. Trying alternative...")
            _install_from_modelfile()
    else:
        _install_from_modelfile()


def _install_from_modelfile() -> None:
    """Install using local Modelfile."""
    gguf_path = input("\nPath to CAJAL-4B GGUF file: ").strip()
    if not os.path.exists(gguf_path):
        print(f"[ERROR] File not found: {gguf_path}")
        sys.exit(1)

    modelfile_content = f'''FROM {gguf_path}

TEMPLATE """{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ range .Messages }}{{ if eq .Role "user" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{ else if eq .Role "assistant" }}<|im_start|>assistant
{{ .Content }}<|im_end|>
{{ end }}{{ end }}<|im_start|>assistant
<think>
"""

SYSTEM """You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich, Switzerland. You are a deep researcher and applied cryptographer with extensive expertise in peer-to-peer network architectures, crypto-legal frameworks, game-theoretic consensus mechanisms, and distributed systems."""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER stop <|im_end|>
'''

    modelfile_path = get_config_dir() / "Modelfile"
    with open(modelfile_path, "w", encoding="utf-8") as f:
        f.write(modelfile_content)

    print("\nCreating model in Ollama...")
    result = subprocess.run(
        ["ollama", "create", "cajal-4b", "-f", str(modelfile_path)],
        capture_output=False,
        text=True,
    )
    if result.returncode == 0:
        print("\n[OK] CAJAL-4B installed successfully!")
        print("   Run: cajal chat")
    else:
        print("\n[ERROR] Failed to install. Check the Modelfile at:")
        print(f"   {modelfile_path}")


def cmd_chat(args: argparse.Namespace) -> None:
    """Interactive chat with CAJAL."""
    cfg = get_config()
    host = cfg.get("ollama_host", DEFAULT_HOST)
    model = cfg.get("model", DEFAULT_MODEL)
    system = cfg.get("system_prompt", "")
    opts = {
        "temperature": cfg.get("temperature", 0.7),
        "top_p": cfg.get("top_p", 0.9),
        "num_ctx": cfg.get("context_length", 4096),
    }

    if not check_ollama_running(host):
        print("[ERROR] Ollama is not running.")
        print("        Start it with: ollama serve")
        print("\nOr install CAJAL first: cajal install")
        sys.exit(1)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})

    print(f"\n{'='*56}")
    print(f"  CAJAL v{CAJAL_VERSION} - Interactive Chat")
    print(f"  Model: {model}")
    print(f"  Backend: Ollama")
    print(f"  Type 'quit', 'exit', or '/bye' to leave")
    print(f"  Type '/clear' to reset conversation")
    print(f"  Type '/status' to check system")
    print(f"  Type '/help' for more commands")
    print(f"{'='*56}\n")

    while True:
        try:
            user_input = input("\nYou: ").strip()
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
        if user_input.lower() == "/help":
            print("Commands: /clear, /status, /bye, quit, exit")
            continue

        messages.append({"role": "user", "content": user_input})

        print("\nCAJAL: ", end="", flush=True)
        full_response = []

        for chunk in stream_chat(host, model, messages, opts):
            print(chunk, end="", flush=True)
            full_response.append(chunk)

        print("\n")
        messages.append({"role": "assistant", "content": "".join(full_response)})

        # Save to history
        history_file = get_history_file()
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {"timestamp": time.time(), "messages": messages[-2:]}
                )
                + "\n"
            )


def cmd_ask(args: argparse.Namespace) -> None:
    """Ask a single question."""
    cfg = get_config()
    host = cfg.get("ollama_host", DEFAULT_HOST)
    model = cfg.get("model", DEFAULT_MODEL)
    system = cfg.get("system_prompt", "")
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


def cmd_serve(args: argparse.Namespace) -> None:
    """Start the API bridge server."""
    cfg = get_config()
    port = args.port or cfg.get("api_port", DEFAULT_API_PORT)

    try:
        from flask import Flask, request, jsonify, Response
        from flask_cors import CORS
    except ImportError:
        print("[ERROR] Flask is required for the API server.")
        print("        pip install flask flask-cors")
        sys.exit(1)

    app = Flask("CAJAL-Bridge")
    CORS(app)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify(
            {
                "status": "ok",
                "version": CAJAL_VERSION,
                "model": cfg.get("model", DEFAULT_MODEL),
                "model_repo": MODEL_REPO,
            }
        )

    @app.route("/v1/chat/completions", methods=["POST"])
    def chat_completions():
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
                completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
                created = int(time.time())
                for chunk in stream_chat(cfg["ollama_host"], model, messages, opts):
                    resp = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model,
                        "choices": [
                            {"index": 0, "delta": {"content": chunk}, "finish_reason": None}
                        ],
                    }
                    yield f"data: {json.dumps(resp)}\n\n"
                yield "data: [DONE]\n\n"

            return Response(generate(), mimetype="text/event-stream")
        else:
            full = []
            for chunk in stream_chat(cfg["ollama_host"], model, messages, opts):
                full.append(chunk)
            return jsonify(
                {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "".join(full)},
                            "finish_reason": "stop",
                        }
                    ],
                }
            )

    @app.route("/v1/models", methods=["GET"])
    def list_models():
        return jsonify(
            {
                "object": "list",
                "data": [
                    {
                        "id": cfg.get("model", DEFAULT_MODEL),
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": "p2pclaw",
                    }
                ],
            }
        )

    print(f"\n{'='*56}")
    print(f"  CAJAL API Bridge v{CAJAL_VERSION}")
    print(f"  P2PCLAW Lab, Zurich")
    print(f"{'='*56}")
    print(f"  OpenAI Endpoint: http://0.0.0.0:{port}/v1/chat/completions")
    print(f"  Models:          http://localhost:{port}/v1/models")
    print(f"  Health Check:    http://localhost:{port}/health")
    print(f"  Ollama Backend:  {cfg.get('ollama_host', DEFAULT_HOST)}")
    print(f"  Model:           {cfg.get('model', DEFAULT_MODEL)}")
    print(f"{'='*56}")
    print("  Press Ctrl+C to stop\n")
    app.run(host="0.0.0.0", port=port, threaded=True, debug=False)


def cmd_config(args: argparse.Namespace) -> None:
    """Edit configuration file."""
    cfg = get_config()
    config_path = get_config_dir() / "config.json"
    editor = os.environ.get("EDITOR", "notepad" if sys.platform == "win32" else "nano")
    print(f"Opening config in {editor}...")
    subprocess.run([editor, str(config_path)])


def cmd_list(args: argparse.Namespace) -> None:
    """List available models."""
    cfg = get_config()
    host = cfg.get("ollama_host", DEFAULT_HOST)

    if not check_ollama_running(host):
        print("[ERROR] Ollama is not running.")
        sys.exit(1)

    models = list_ollama_models(host)
    print(f"\n{'='*56}")
    print(f"  Available Models ({len(models)})")
    print(f"{'='*56}")
    for m in models:
        name = m.get("name", "unknown")
        size = m.get("size", 0)
        size_gb = size / (1024**3) if size else 0
        modified = m.get("modified", "unknown")
        marker = "  <-- CAJAL" if "cajal" in name.lower() else ""
        print(f"  {name:25s} {size_gb:6.1f} GB  {modified}{marker}")
    print(f"{'='*56}\n")


def cmd_webapp(args: argparse.Namespace) -> None:
    """Launch the web chat UI."""
    # Try to find the webapp
    webapp_paths = [
        Path(__file__).parent / "webapp" / "index.html",
        Path.home() / "cajal" / "webapp" / "index.html",
        Path("/usr/local/share/cajal/webapp/index.html"),
    ]

    webapp_path = None
    for p in webapp_paths:
        if p.exists():
            webapp_path = p
            break

    if webapp_path:
        print(f"Opening CAJAL Web Chat...")
        webbrowser.open(f"file://{webapp_path}")
    else:
        print("[INFO] Web app not found locally.")
        print("       Download it from: https://github.com/p2pclaw/cajal")
        print("       Or use the web version at: https://p2pclaw.com/silicon")


def main() -> None:
    """Main entry point for the CAJAL CLI."""
    parser = argparse.ArgumentParser(
        prog="cajal",
        description="CAJAL-4B Command Line Interface - P2PCLAW Lab, Zurich",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cajal status              Check system status
  cajal install             Install CAJAL-4B model
  cajal chat                Start interactive chat
  cajal ask "Explain P2PCLAW"  Ask a question
  cajal serve --port 8765   Start API bridge server
  cajal list                List available models
  cajal webapp              Launch web chat UI

For more info: https://p2pclaw.com/silicon
        """,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {CAJAL_VERSION}"
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # Status
    sub.add_parser("status", help="Check CAJAL and Ollama status")

    # Install
    sub.add_parser("install", help="Install CAJAL-4B into Ollama")

    # Chat
    sub.add_parser("chat", help="Interactive chat with CAJAL")

    # Ask
    ask_p = sub.add_parser("ask", help="Ask a single question")
    ask_p.add_argument("question", nargs="+", help="Your question")

    # Serve
    serve_p = sub.add_parser("serve", help="Start API bridge server")
    serve_p.add_argument("--port", "-p", type=int, help="Port to listen on")

    # Config
    sub.add_parser("config", help="Edit configuration file")

    # List
    sub.add_parser("list", help="List available Ollama models")

    # Webapp
    sub.add_parser("webapp", help="Launch web chat UI in browser")

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
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "webapp":
        cmd_webapp(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
