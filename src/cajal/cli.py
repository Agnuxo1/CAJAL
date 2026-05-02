"""CAJAL CLI — Command Line Interface."""

import argparse
import io
import json
import os
import subprocess
import sys
import time

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pathlib import Path

import requests

from .config import get_config, save_config, DEFAULT_CONFIG
from .core import CAJAL

__version__ = "1.0.0"

def check_ollama_running(host):
    try:
        r = requests.get(f"{host}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

def stream_chat(host, model, messages, options=None):
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
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

def cmd_status(args):
    cfg = get_config()
    host = cfg.get("ollama_host", "http://localhost:11434")
    model = cfg.get("model", "cajal-4b")
    
    print(f"\n{'='*50}")
    print(f"  CAJAL CLI v{__version__} — Status")
    print(f"{'='*50}")
    
    if check_ollama_running(host):
        print(f"  Ollama:         {host} ✅ Running")
        try:
            models = requests.get(f"{host}/api/tags", timeout=5).json().get("models", [])
            cajal_found = any(m.get("name", "").startswith("cajal") for m in models)
            print(f"  CAJAL Model:    {'✅ Installed' if cajal_found else '❌ Not found'}")
            if not cajal_found:
                print(f"  Run:            cajal install")
            print(f"  Other models:   {len(models)}")
        except Exception:
            pass
    else:
        print(f"  Ollama:         {host} ❌ Not running")
        print(f"  Install:        https://ollama.com/download")
    
    print(f"  Config:         {Path.home() / '.cajal' / 'config.json'}")
    print(f"  Backend:        Ollama API")
    print(f"{'='*50}\n")

def cmd_install(args):
    cfg = get_config()
    host = cfg.get("ollama_host", "http://localhost:11434")
    
    if not check_ollama_running(host):
        print("[ERROR] Ollama is not running. Please start it first: ollama serve")
        sys.exit(1)
    
    print("CAJAL-4B Installation")
    print("-" * 40)
    print("This will create the 'cajal-4b' model in Ollama.")
    print("Ensure the GGUF file is available.")
    print()
    
    confirm = input("Proceed? [Y/n]: ").strip().lower()
    if confirm and confirm not in ("y", "yes"):
        print("Cancelled.")
        return
    
    print("Creating model in Ollama...")
    result = subprocess.run(
        ["ollama", "create", "cajal-4b", "-f", "-"],
        input=create_modelfile(),
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("✅ CAJAL-4B installed successfully!")
        print("   Run: cajal chat")
    else:
        print("[ERROR] Failed to install:")
        print(result.stderr)

def create_modelfile():
    return """FROM ./CAJAL-4B-f16.gguf

TEMPLATE """{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ range .Messages }}{{ if eq .Role \"user\" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{ else if eq .Role \"assistant\" }}<|im_start|>assistant
{{ .Content }}<|im_end|>
{{ end }}{{ end }}<|im_start|>assistant
<think>
"""

SYSTEM """You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland..."""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER stop <|im_end|>
"""

def cmd_chat(args):
    cfg = get_config()
    host = cfg.get("ollama_host", "http://localhost:11434")
    model = cfg.get("model", "cajal-4b")
    system = cfg.get("system_prompt", DEFAULT_CONFIG["system_prompt"])
    opts = {
        "temperature": cfg.get("temperature", 0.7),
        "top_p": cfg.get("top_p", 0.9),
        "num_ctx": cfg.get("context_length", 4096),
    }
    
    if not check_ollama_running(host):
        print("[ERROR] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)
    
    messages = [{"role": "system", "content": system}]
    
    print(f"\n{'='*60}")
    print(f"  CAJAL v{__version__} — Interactive Chat")
    print(f"  Model: {model} | Backend: Ollama")
    print(f"  Type 'quit', 'exit', or '/bye' to leave")
    print(f"  Type '/clear' to reset conversation")
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
            messages = [{"role": "system", "content": system}]
            print("[Conversation cleared]")
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        print("\n🤖 CAJAL: ", end="", flush=True)
        full_response = []
        
        for chunk in stream_chat(host, model, messages, opts):
            print(chunk, end="", flush=True)
            full_response.append(chunk)
        
        print("\n")
        messages.append({"role": "assistant", "content": "".join(full_response)})
        
        # Save history
        history_file = Path.home() / ".cajal" / "history.jsonl"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": time.time(), "messages": messages[-2:]}) + "\n")

def cmd_ask(args):
    cfg = get_config()
    host = cfg.get("ollama_host", "http://localhost:11434")
    model = cfg.get("model", "cajal-4b")
    system = cfg.get("system_prompt", DEFAULT_CONFIG["system_prompt"])
    opts = {
        "temperature": cfg.get("temperature", 0.7),
        "top_p": cfg.get("top_p", 0.9),
        "num_ctx": cfg.get("context_length", 4096),
    }
    
    question = " ".join(args.question)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question}
    ]
    
    if not check_ollama_running(host):
        print("[ERROR] Ollama is not running.", file=sys.stderr)
        sys.exit(1)
    
    for chunk in stream_chat(host, model, messages, opts):
        print(chunk, end="", flush=True)
    print()

def cmd_config(args):
    editor = os.environ.get("EDITOR", "notepad" if sys.platform == "win32" else "nano")
    config_path = Path.home() / ".cajal" / "config.json"
    print(f"Opening config in {editor}...")
    subprocess.run([editor, str(config_path)])

def main():
    parser = argparse.ArgumentParser(
        prog="cajal",
        description="CAJAL-4B Command Line Interface"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    sub = parser.add_subparsers(dest="command", help="Commands")
    
    sub.add_parser("status", help="Check CAJAL and Ollama status")
    sub.add_parser("install", help="Install CAJAL-4B into Ollama")
    sub.add_parser("chat", help="Interactive chat with CAJAL")
    sub.add_parser("config", help="Edit configuration file")
    
    ask_p = sub.add_parser("ask", help="Ask a single question")
    ask_p.add_argument("question", nargs="+", help="Your question")
    
    args = parser.parse_args()
    
    if args.command == "status":
        cmd_status(args)
    elif args.command == "install":
        cmd_install(args)
    elif args.command == "chat":
        cmd_chat(args)
    elif args.command == "ask":
        cmd_ask(args)
    elif args.command == "config":
        cmd_config(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
