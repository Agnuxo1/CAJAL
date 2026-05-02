"""CAJAL OpenAI-compatible API server."""

import argparse
import json
import sys

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from .config import get_config
from .core import CAJAL

def create_app():
    app = Flask("CAJAL-Server")
    CORS(app)
    cfg = get_config()
    
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "version": "1.0.0",
            "model": cfg.get("model", "cajal-4b"),
            "backend": "ollama-bridge"
        })
    
    @app.route("/v1/models", methods=["GET"])
    def list_models():
        return jsonify({
            "object": "list",
            "data": [{
                "id": "cajal-4b",
                "object": "model",
                "created": 1714608000,
                "owned_by": "p2pclaw"
            }]
        })
    
    @app.route("/v1/chat/completions", methods=["POST"])
    def chat_completions():
        data = request.get_json(force=True)
        messages = data.get("messages", [])
        model = data.get("model", cfg.get("model", "cajal-4b"))
        stream = data.get("stream", True)
        temperature = data.get("temperature", cfg.get("temperature", 0.7))
        max_tokens = data.get("max_tokens", cfg.get("context_length", 4096))
        
        if stream:
            def generate():
                cajal = CAJAL.from_ollama(
                    host=cfg.get("ollama_host", "http://localhost:11434"),
                    model=model
                )
                for chunk in cajal.stream_chat(
                    message=messages[-1]["content"] if messages else "",
                    system=messages[0]["content"] if messages and messages[0]["role"] == "system" else None,
                    temperature=temperature,
                    max_tokens=max_tokens
                ):
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}}]})}\n\n"
                yield "data: [DONE]\n\n"
            return Response(generate(), mimetype="text/event-stream")
        else:
            cajal = CAJAL.from_ollama(
                host=cfg.get("ollama_host", "http://localhost:11434"),
                model=model
            )
            response = cajal.chat(
                message=messages[-1]["content"] if messages else "",
                system=messages[0]["content"] if messages and messages[0]["role"] == "system" else None,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return jsonify({
                "id": "cajal-chat-001",
                "object": "chat.completion",
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": response},
                    "finish_reason": "stop"
                }]
            })
    
    @app.route("/v1/completions", methods=["POST"])
    def completions():
        data = request.get_json(force=True)
        prompt = data.get("prompt", "")
        return jsonify({
            "id": "cajal-comp-001",
            "object": "text_completion",
            "model": cfg.get("model", "cajal-4b"),
            "choices": [{"text": prompt, "index": 0, "finish_reason": "stop"}]
        })
    
    return app

def main():
    parser = argparse.ArgumentParser(description="CAJAL API Server")
    parser.add_argument("--port", "-p", type=int, default=8765, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()
    
    app = create_app()
    print(f"🚀 CAJAL API Server running on http://{args.host}:{args.port}")
    print(f"   OpenAI-compatible endpoint: http://localhost:{args.port}/v1/chat/completions")
    print(f"   Health check:               http://localhost:{args.port}/health")
    print(f"   Press Ctrl+C to stop\n")
    app.run(host=args.host, port=args.port, threaded=True)

if __name__ == "__main__":
    main()
