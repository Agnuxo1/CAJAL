#!/usr/bin/env python3
"""
CAJAL Local API Server
=================================
Servidor FastAPI con soporte vLLM para desplegar CAJAL localmente.
Soporta modelos LoRA (vía unsloth/vLLM) y GGUF (vía llama-cpp-python).

Endpoints:
  - POST /v1/chat/completions   (OpenAI-compatible)
  - POST /v1/completions          (OpenAI-compatible)
  - GET  /v1/models               (OpenAI-compatible)
  - POST /generate_paper          (Especializado P2PCLAW)

Autor: CAJAL Team
"""

import os
import sys
import time
import json
import uuid
import logging
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncIterator, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("p2pclaw-server")

# ---------------------------------------------------------------------------
# Imports condicionales (FastAPI, vLLM, etc.)
# ---------------------------------------------------------------------------
try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
    from fastapi.responses import StreamingResponse, JSONResponse
    from pydantic import BaseModel, Field
except ImportError:
    logger.error("FastAPI/uvicorn no instalados. Ejecute: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Modelos Pydantic para requests/responses
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "cajal"
    messages: List[ChatMessage]
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    max_tokens: int = 4096
    stream: bool = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    thinking_mode: bool = False  # P2PClaw: habilitar thinking de Qwen3


class CompletionRequest(BaseModel):
    model: str = "cajal"
    prompt: Union[str, List[str]]
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 4096
    stream: bool = False
    stop: Optional[Union[str, List[str]]] = None
    echo: bool = False


class GeneratePaperRequest(BaseModel):
    topic: str
    sections: Optional[List[str]] = None
    max_tokens: int = 8192
    include_references: bool = True
    latex_format: bool = True
    style: str = "academic"  # academic, survey, technical_note


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "cajal"


class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


# ---------------------------------------------------------------------------
# Configuración del servidor
# ---------------------------------------------------------------------------

@dataclass
class ServerConfig:
    model_path: str
    model_type: str  # "hf", "gguf", "lora"
    lora_path: Optional[str] = None
    host: str = "0.0.0.0"
    port: int = 8000
    context_length: int = 32768
    gpu_memory_utilization: float = 0.90
    tensor_parallel_size: int = 1
    dtype: str = "auto"
    chat_template: Optional[str] = None
    system_prompt: str = (
        "You are CAJAL, an expert AI assistant specialized in peer-to-peer "
        "networks, distributed systems, game theory, mechanism design, and legal-tech "
        "intersections. Provide rigorous, well-cited research assistance."
    )
    max_model_len: Optional[int] = None


# ---------------------------------------------------------------------------
# Engine Factory: carga modelo según tipo
# ---------------------------------------------------------------------------

class ModelEngine:
    """Abstracción del motor de inferencia."""

    def __init__(self, config: ServerConfig):
        self.cfg = config
        self.model_name = Path(config.model_path).name
        self.llm = None
        self.tokenizer = None
        self.sampling_params_class = None

    def load(self):
        logger.info(f"[ENGINE] Cargando modelo tipo='{self.cfg.model_type}' desde {self.cfg.model_path}")
        t0 = time.time()

        if self.cfg.model_type == "gguf":
            self._load_gguf()
        elif self.cfg.model_type in ("hf", "lora"):
            self._load_vllm()
        else:
            raise ValueError(f"model_type no soportado: {self.cfg.model_type}")

        logger.info(f"[ENGINE] Modelo cargado en {time.time() - t0:.2f}s")

    # ------------------------------------------------------------------
    # Carga vLLM (HF o LoRA)
    # ------------------------------------------------------------------
    def _load_vllm(self):
        try:
            from vllm import LLM, SamplingParams
            from vllm.lora.request import LoRARequest
        except ImportError:
            logger.error("vLLM no instalado. Ejecute: pip install vllm")
            sys.exit(1)

        self.sampling_params_class = SamplingParams
        self.LoRARequest = LoRARequest

        kwargs = {
            "model": self.cfg.model_path,
            "tensor_parallel_size": self.cfg.tensor_parallel_size,
            "gpu_memory_utilization": self.cfg.gpu_memory_utilization,
            "dtype": self.cfg.dtype,
            "max_model_len": self.cfg.max_model_len or self.cfg.context_length,
        }

        if self.cfg.chat_template:
            kwargs["chat_template"] = self.cfg.chat_template

        self.llm = LLM(**kwargs)
        self.tokenizer = self.llm.get_tokenizer()

        # Precargar LoRA si existe
        if self.cfg.lora_path:
            logger.info(f"[ENGINE] Precargando LoRA: {self.cfg.lora_path}")
            self.lora_request = LoRARequest(
                lora_name="p2pclaw_lora",
                lora_int_id=1,
                lora_local_path=self.cfg.lora_path,
            )
        else:
            self.lora_request = None

    # ------------------------------------------------------------------
    # Carga GGUF (llama-cpp-python)
    # ------------------------------------------------------------------
    def _load_gguf(self):
        try:
            from llama_cpp import Llama
        except ImportError:
            logger.error("llama-cpp-python no instalado. Ejecute: CMAKE_ARGS='-DLLAMA_CUDA=on' pip install llama-cpp-python")
            sys.exit(1)

        self.llm = Llama(
            model_path=self.cfg.model_path,
            n_ctx=self.cfg.context_length,
            n_gpu_layers=-1,  # offload all layers a GPU
            verbose=False,
            chat_format="chatml",  # compatible con Qwen/DeepSeek
        )
        self.tokenizer = None  # llama-cpp maneja tokenización interna
        self.lora_request = None

    # ------------------------------------------------------------------
    # Métodos de inferencia
    # ------------------------------------------------------------------
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.cfg.model_type == "gguf":
            return self._chat_gguf(messages, **kwargs)
        return self._chat_vllm(messages, **kwargs)

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[str]:
        if self.cfg.model_type == "gguf":
            return self._chat_stream_gguf(messages, **kwargs)
        return self._chat_stream_vllm(messages, **kwargs)

    # ----- vLLM -------------------------------------------------------
    def _chat_vllm(self, messages, **kwargs):
        from vllm import SamplingParams

        sp = SamplingParams(
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.9),
            top_k=kwargs.get("top_k", 40),
            max_tokens=kwargs.get("max_tokens", 4096),
            stop=kwargs.get("stop", []),
            presence_penalty=kwargs.get("presence_penalty", 0.0),
            frequency_penalty=kwargs.get("frequency_penalty", 0.0),
        )

        outputs = self.llm.chat(
            messages,
            sampling_params=sp,
            lora_request=self.lora_request,
            use_tqdm=False,
        )
        return outputs[0].outputs[0].text

    async def _chat_stream_vllm(self, messages, **kwargs):
        from vllm import SamplingParams

        sp = SamplingParams(
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.9),
            top_k=kwargs.get("top_k", 40),
            max_tokens=kwargs.get("max_tokens", 4096),
            stop=kwargs.get("stop", []),
        )

        # vLLM streaming vía async generator
        streamer = self.llm.chat(
            messages,
            sampling_params=sp,
            lora_request=self.lora_request,
            stream=True,
        )
        for chunk in streamer:
            text = chunk.outputs[0].text
            if text:
                yield text

    # ----- GGUF -------------------------------------------------------
    def _chat_gguf(self, messages, **kwargs):
        response = self.llm.create_chat_completion(
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.9),
            max_tokens=kwargs.get("max_tokens", 4096),
            stop=kwargs.get("stop", []),
            stream=False,
        )
        return response["choices"][0]["message"]["content"]

    async def _chat_stream_gguf(self, messages, **kwargs):
        stream = self.llm.create_chat_completion(
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.9),
            max_tokens=kwargs.get("max_tokens", 4096),
            stop=kwargs.get("stop", []),
            stream=True,
        )
        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta and delta["content"]:
                yield delta["content"]

    # ------------------------------------------------------------------
    # Completion (no chat)
    # ------------------------------------------------------------------
    def complete(self, prompt: str, **kwargs) -> str:
        if self.cfg.model_type == "gguf":
            response = self.llm(prompt, **self._gguf_params(**kwargs))
            return response["choices"][0]["text"]

        from vllm import SamplingParams
        sp = SamplingParams(
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.9),
            max_tokens=kwargs.get("max_tokens", 4096),
            stop=kwargs.get("stop", []),
        )
        outputs = self.llm.generate(prompt, sampling_params=sp, lora_request=self.lora_request)
        return outputs[0].outputs[0].text

    def _gguf_params(self, **kwargs):
        return {
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stop": kwargs.get("stop", []),
        }

    # ------------------------------------------------------------------
    # Thinking mode (Qwen3 especial)
    # ------------------------------------------------------------------
    def apply_thinking_mode(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Envuelve el prompt para forzar thinking de Qwen3."""
        # Detectar si ya tiene thinking
        has_thinking = any("<|thinking|>" in m.get("content", "") for m in messages)
        if has_thinking:
            return messages

        # Añadir instruction de thinking en system
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] += (
                "\n\nBefore answering, wrap your reasoning inside `<|thinking|>`...`<|/thinking|>` tags. "
                "Think step-by-step about the problem, cite relevant concepts, and then provide your final answer."
            )
        else:
            messages.insert(0, {
                "role": "system",
                "content": self.cfg.system_prompt + (
                    "\n\nBefore answering, wrap your reasoning inside `<|thinking|>`...`<|/thinking|>` tags. "
                    "Think step-by-step about the problem, cite relevant concepts, and then provide your final answer."
                ),
            })
        return messages

    # ------------------------------------------------------------------
    # Tool use
    # ------------------------------------------------------------------
    def apply_tools(self, messages: List[Dict[str, str]], tools: List[Dict], tool_choice) -> List[Dict[str, str]]:
        """Prepara el prompt para tool use (simplificado, similar a OpenAI function calling)."""
        if not tools:
            return messages

        tool_desc = "\n\nYou have access to the following tools:\n"
        for tool in tools:
            tool_desc += f"- {tool['function']['name']}: {tool['function'].get('description', '')}\n"
        tool_desc += (
            "\nIf you need to use a tool, respond with a JSON object inside "
            "`<|tool_call|>` tags like: `<|tool_call|>{\"name\": \"...\", \"arguments\": {...}}<|/tool_call|>`"
        )

        if messages and messages[0]["role"] == "system":
            messages[0]["content"] += tool_desc
        else:
            messages.insert(0, {"role": "system", "content": self.cfg.system_prompt + tool_desc})
        return messages


# ---------------------------------------------------------------------------
# Estado global del servidor
# ---------------------------------------------------------------------------

engine: Optional[ModelEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    logger.info("[LIFESPAN] Iniciando servidor CAJAL...")
    if engine is None:
        raise RuntimeError("Engine no inicializado. Llame a init_engine() antes.")
    engine.load()
    logger.info(f"[LIFESPAN] Servidor listo en http://{engine.cfg.host}:{engine.cfg.port}")
    yield
    logger.info("[LIFESPAN] Apagando servidor...")


app = FastAPI(
    title="CAJAL API",
    description="API local compatible con OpenAI para CAJAL",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Middleware: logging de requests
# ---------------------------------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    client = request.client.host if request.client else "unknown"
    logger.info(f"[REQ] {client} | {request.method} {request.url.path}")
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(f"[RES] {client} | {request.method} {request.url.path} | {response.status_code} | {duration:.1f}ms")
    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": engine is not None and engine.llm is not None}


@app.get("/v1/models", response_model=ModelListResponse)
async def list_models():
    return ModelListResponse(data=[
        ModelInfo(
            id=engine.cfg.model_path,
            created=int(time.time()),
        )
    ])


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if engine is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    # Añadir system prompt si no está presente
    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": engine.cfg.system_prompt})

    # Thinking mode
    if request.thinking_mode:
        messages = engine.apply_thinking_mode(messages)

    # Tool use
    if request.tools:
        messages = engine.apply_tools(messages, request.tools, request.tool_choice)

    gen_kwargs = {
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
        "max_tokens": request.max_tokens,
        "stop": request.stop or [],
        "presence_penalty": request.presence_penalty,
        "frequency_penalty": request.frequency_penalty,
    }

    request_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())

    if request.stream:
        async def stream_generator():
            accumulated = ""
            async for chunk in engine.chat_stream(messages, **gen_kwargs):
                accumulated += chunk
                data = {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": request.model,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                yield f"data: {json.dumps(data)}\n\n"
            # Final chunk
            yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created, 'model': request.model, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    # Non-streaming
    text = engine.chat(messages, **gen_kwargs)
    return JSONResponse({
        "id": request_id,
        "object": "chat.completion",
        "created": created,
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": text},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": -1,  # vLLM/llama-cpp pueden proveer esto
            "completion_tokens": -1,
            "total_tokens": -1,
        },
    })


@app.post("/v1/completions")
async def completions(request: CompletionRequest):
    if engine is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")

    prompt = request.prompt if isinstance(request.prompt, str) else request.prompt[0]
    gen_kwargs = {
        "temperature": request.temperature,
        "top_p": request.top_p,
        "max_tokens": request.max_tokens,
        "stop": request.stop or [],
    }

    request_id = f"cmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())

    if request.stream:
        async def stream_gen():
            accumulated = ""
            # llama-cpp no tiene stream nativo para completion simple, usar chat_stream con un solo mensaje user
            messages = [{"role": "user", "content": prompt}]
            async for chunk in engine.chat_stream(messages, **gen_kwargs):
                accumulated += chunk
                data = {
                    "id": request_id,
                    "object": "text_completion.chunk",
                    "created": created,
                    "model": request.model,
                    "choices": [{"index": 0, "text": chunk, "finish_reason": None}],
                }
                yield f"data: {json.dumps(data)}\n\n"
            yield f"data: {json.dumps({'id': request_id, 'object': 'text_completion.chunk', 'created': created, 'model': request.model, 'choices': [{'index': 0, 'text': '', 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_gen(), media_type="text/event-stream")

    text = engine.complete(prompt, **gen_kwargs)
    return JSONResponse({
        "id": request_id,
        "object": "text_completion",
        "created": created,
        "model": request.model,
        "choices": [{"index": 0, "text": text, "finish_reason": "stop"}],
    })


@app.post("/generate_paper")
async def generate_paper(request: GeneratePaperRequest):
    """Endpoint especializado para generar borradores de papers académicos."""
    if engine is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")

    sections = request.sections or ["Abstract", "Introduction", "Related Work", "Model/Protocol", "Analysis", "Conclusion", "References"]

    paper_prompt = (
        f"Generate a rigorous academic paper draft on the topic: '{request.topic}'.\n\n"
        f"Style: {request.style}\n"
        f"Format: {'LaTeX' if request.latex_format else 'Markdown'}\n"
        f"Include references: {request.include_references}\n\n"
        f"Structure with the following sections: {', '.join(sections)}.\n\n"
        f"Provide mathematical derivations where applicable, cite key papers in the field, "
        f"and ensure the protocol description is formal and unambiguous."
    )

    messages = [
        {"role": "system", "content": engine.cfg.system_prompt},
        {"role": "user", "content": paper_prompt},
    ]

    text = engine.chat(messages, temperature=0.6, top_p=0.9, max_tokens=request.max_tokens)

    return {
        "topic": request.topic,
        "style": request.style,
        "format": "latex" if request.latex_format else "markdown",
        "sections": sections,
        "paper": text,
        "model": engine.cfg.model_path,
    }


# ---------------------------------------------------------------------------
# Inicialización y CLI
# ---------------------------------------------------------------------------

def init_engine(cfg: ServerConfig) -> ModelEngine:
    global engine
    engine = ModelEngine(cfg)
    return engine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deploy_local_server.py",
        description="Servidor API local para CAJAL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Desplegar modelo HuggingFace (ya fusionado o base)
  python deploy_local_server.py --model ./merged_model --type hf

  # Desplegar con LoRA sobre modelo base
  python deploy_local_server.py --model Qwen/Qwen2.5-14B-Instruct --type lora --lora ./lora_adapter

  # Desplegar GGUF
  python deploy_local_server.py --model ./cajal-q4_k_m.gguf --type gguf

  # Múltiples GPUs
  python deploy_local_server.py --model ./model --type hf --tensor-parallel 2
        """,
    )
    parser.add_argument("--model", required=True, help="Ruta al modelo (HF, GGUF, o identificador HuggingFace)")
    parser.add_argument("--type", required=True, choices=["hf", "gguf", "lora"], help="Tipo de modelo")
    parser.add_argument("--lora", default=None, help="Ruta a adaptador LoRA (solo con --type lora)")
    parser.add_argument("--host", default="0.0.0.0", help="Host para escuchar")
    parser.add_argument("--port", type=int, default=8000, help="Puerto")
    parser.add_argument("--context-length", type=int, default=32768, help="Longitud de contexto máxima")
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.90, help="Fracción de VRAM a usar (vLLM)")
    parser.add_argument("--tensor-parallel", type=int, default=1, help="Tamaño de paralelismo tensorial")
    parser.add_argument("--dtype", default="auto", choices=["auto", "float16", "bfloat16", "float32"], help="Tipo de datos")
    parser.add_argument("--chat-template", default=None, help="Ruta a archivo de chat template")
    parser.add_argument("--system-prompt", default=None, help="System prompt personalizado")
    parser.add_argument("--max-model-len", type=int, default=None, help="Máxima longitud de secuencia del modelo")
    return parser


def main():
    args = build_parser().parse_args()

    # Auto-detectar LoRA si se pasó --lora sin --type lora
    model_type = args.type
    if args.lora and model_type == "hf":
        logger.info("[INFO] Se detectó --lora con --type hf. Cambiando a --type lora")
        model_type = "lora"

    cfg = ServerConfig(
        model_path=args.model,
        model_type=model_type,
        lora_path=args.lora,
        host=args.host,
        port=args.port,
        context_length=args.context_length,
        gpu_memory_utilization=args.gpu_memory_utilization,
        tensor_parallel_size=args.tensor_parallel,
        dtype=args.dtype,
        chat_template=args.chat_template,
        system_prompt=args.system_prompt or (
            "You are CAJAL, an expert AI assistant specialized in peer-to-peer "
            "networks, distributed systems, game theory, mechanism design, and legal-tech "
            "intersections (P2P + CLAW). You provide rigorous, well-cited research assistance, "
            "generate LaTeX-formatted paper drafts, perform mathematical derivations, and "
            "analyze protocol incentives with formal precision. Always think step-by-step and "
            "cite sources when possible."
        ),
        max_model_len=args.max_model_len,
    )

    init_engine(cfg)
    uvicorn.run(app, host=cfg.host, port=cfg.port, log_level="info")


if __name__ == "__main__":
    main()
