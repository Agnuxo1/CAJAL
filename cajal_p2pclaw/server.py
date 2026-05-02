import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import argparse

from .model import CAJALModel, DEFAULT_MODEL

app = FastAPI(title="CAJAL API", version="1.0.0")
model = None

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model: str

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest):
    global model
    if model is None:
        model = CAJALModel()
    
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    response = model.generate(
        messages=messages,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        system_prompt=request.system_prompt,
    )
    
    return ChatResponse(response=response, model=DEFAULT_MODEL)

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": DEFAULT_MODEL,
                "object": "model",
                "owned_by": "p2pclaw",
            }
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok", "model": DEFAULT_MODEL}

def main():
    parser = argparse.ArgumentParser(description="CAJAL FastAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID")
    args = parser.parse_args()
    
    print(f"[CAJAL] Starting server on {args.host}:{args.port}")
    print(f"[CAJAL] Model: {args.model}")
    print(f"[CAJAL] OpenAI-compatible endpoint: http://{args.host}:{args.port}/v1/chat/completions")
    
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
