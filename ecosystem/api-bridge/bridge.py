#!/usr/bin/env python3
"""
CAJAL API Bridge

A lightweight OpenAI-compatible API server that proxies requests
to the local Ollama instance running CAJAL-4B.

This enables any tool expecting an OpenAI-compatible API
to use CAJAL-4B locally.

Endpoints:
    GET  /health                    → Health check
    POST /v1/chat/completions       → OpenAI-compatible chat
    POST /v1/completions            → OpenAI-compatible completions
    GET  /v1/models                 → List available models
    POST /api/chat                  → Ollama-native chat

Usage:
    python bridge.py
    python bridge.py --port 8765
    python bridge.py --host 0.0.0.0 --port 8765
"""

import argparse
import json
import time
import uuid
import sys
from pathlib import Path

try:
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS
except ImportError:
    print("[ERROR] Required packages not installed.")
    print("        pip install flask flask-cors")
    sys.exit(1)

import requests

app = Flask("CAJAL-Bridge")
CORS(app)

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "cajal-4b"
BRIDGE_VERSION = "1.0.0"


def load_config():
    """Load CAJAL config if available."""
    cfg_path = Path.home() / ".cajal" / "config.json"
    if cfg_path.exists():
        return json.loads(cfg_path.read_text())
    return {
        "model": DEFAULT_MODEL,
        "ollama_host": DEFAULT_HOST,
        "temperature": 0.7,
        "top_p": 0.9,
        "context_length": 4096,
    }


def check_ollama(host):
    try:
        r = requests.get(f"{host}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def stream_ollama_chat(host, model, messages, options):
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": options,
    }
    with requests.post(f"{host}/api/chat", json=payload, stream=True, timeout=300) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if line:
                yield json.loads(line)


@app.route("/health", methods=["GET"])
def health():
    cfg = load_config()
    ollama_ok = check_ollama(cfg.get("ollama_host", DEFAULT_HOST))
    return jsonify({
        "status": "ok" if ollama_ok else "degraded",
        "bridge_version": BRIDGE_VERSION,
        "ollama_connected": ollama_ok,
        "model": cfg.get("model", DEFAULT_MODEL),
    })


@app.route("/v1/models", methods=["GET"])
def list_models():
    cfg = load_config()
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": cfg.get("model", DEFAULT_MODEL),
                "object": "model",
                "created": int(time.time()),
                "owned_by": "p2pclaw",
            }
        ],
    })


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    cfg = load_config()
    data = request.get_json(force=True)

    messages = data.get("messages", [])
    model = data.get("model", cfg.get("model", DEFAULT_MODEL))
    stream = data.get("stream", True)
    temperature = data.get("temperature", cfg.get("temperature", 0.7))
    top_p = data.get("top_p", cfg.get("top_p", 0.9))
    max_tokens = data.get("max_tokens", cfg.get("context_length", 4096))

    options = {
        "temperature": temperature,
        "top_p": top_p,
        "num_ctx": max_tokens,
    }

    if not check_ollama(cfg.get("ollama_host", DEFAULT_HOST)):
        return jsonify({"error": "Ollama not running"}), 503

    if stream:
        def generate():
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
            created = int(time.time())
            for chunk in stream_ollama_chat(
                cfg.get("ollama_host", DEFAULT_HOST), model, messages, options
            ):
                if "message" in chunk and "content" in chunk["message"]:
                    delta = {"content": chunk["message"]["content"]}
                    resp = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model,
                        "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
                    }
                    yield f"data: {json.dumps(resp)}\n\n"
            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype="text/event-stream")
    else:
        full = []
        for chunk in stream_ollama_chat(
            cfg.get("ollama_host", DEFAULT_HOST), model, messages, options
        ):
            if "message" in chunk and "content" in chunk["message"]:
                full.append(chunk["message"]["content"])

        return jsonify({
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
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        })


@app.route("/v1/completions", methods=["POST"])
def completions():
    """Legacy completions endpoint — maps to chat."""
    data = request.get_json(force=True)
    prompt = data.get("prompt", "")
    data["messages"] = [{"role": "user", "content": prompt}]
    request._cached_json = data
    return chat_completions()


@app.route("/api/chat", methods=["POST"])
def ollama_chat():
    """Native Ollama API passthrough."""
    cfg = load_config()
    data = request.get_json(force=True)
    stream = data.get("stream", True)

    if not check_ollama(cfg.get("ollama_host", DEFAULT_HOST)):
        return jsonify({"error": "Ollama not running"}), 503

    if stream:
        def generate():
            with requests.post(
                f"{cfg.get('ollama_host', DEFAULT_HOST)}/api/chat",
                json=data, stream=True, timeout=300
            ) as r:
                for line in r.iter_lines():
                    if line:
                        yield line.decode("utf-8") + "\n"
        return Response(generate(), mimetype="application/x-ndjson")
    else:
        r = requests.post(
            f"{cfg.get('ollama_host', DEFAULT_HOST)}/api/chat",
            json=data, timeout=300
        )
        return jsonify(r.json())


def main():
    parser = argparse.ArgumentParser(description="CAJAL API Bridge")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", "-p", type=int, default=8765, help="Port to listen on")
    args = parser.parse_args()

    cfg = load_config()
    print(f"""
╔═══════════════════════════════════════════════════════╗
║  CAJAL API Bridge v{BRIDGE_VERSION}                          ║
║  P2PCLAW Lab, Zurich | https://p2pclaw.com/silicon    ║
╠═══════════════════════════════════════════════════════╣
║  OpenAI Endpoint: http://{args.host}:{args.port:<5}/v1/chat/completions ║
║  Health Check:    http://localhost:{args.port}/health           ║
║  Ollama Backend:  {cfg.get('ollama_host', DEFAULT_HOST):<42} ║
║  Default Model:   {cfg.get('model', DEFAULT_MODEL):<42} ║
╚═══════════════════════════════════════════════════════╝
Press Ctrl+C to stop
""")
    app.run(host=args.host, port=args.port, threaded=True, debug=False)


if __name__ == "__main__":
    main()
