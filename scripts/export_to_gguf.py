#!/usr/bin/env python3
"""
CAJAL GGUF Export Script
====================================
Exporta modelos fine-tuned a múltiples formatos GGUF con diferentes niveles de cuantización.
Soporta modelos LoRA (auto-merge) y modelos ya fusionados (merged).

Autor: CAJAL Team
Requiere: unsloth, transformers, llama.cpp (convert.py / convert-hf-to-gguf.py)
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# ---------------------------------------------------------------------------
# Configuración de cuantizaciones soportadas
# ---------------------------------------------------------------------------

QUANTIZATION_LEVELS = {
    "q4_k_m": {
        "method": "Q4_K_M",
        "description": "4-bit, método K-quantización medio",
        "quality": "★★★☆☆ Alta calidad para chat y RAG",
        "size_factor": 0.28,
        "recommended": True,
    },
    "q5_k_m": {
        "method": "Q5_K_M",
        "description": "5-bit, método K-quantización medio",
        "quality": "★★★★☆ Muy alta calidad, ideal para reasoning",
        "size_factor": 0.34,
        "recommended": False,
    },
    "q8_0": {
        "method": "Q8_0",
        "description": "8-bit, cuantización lineal",
        "quality": "★★★★★ Casi lossless, mínima pérdida",
        "size_factor": 0.53,
        "recommended": False,
    },
    "f16": {
        "method": "F16",
        "description": "16-bit flotante, sin cuantizar",
        "quality": "★★★★★ Perfecto, máxima calidad",
        "size_factor": 1.0,
        "recommended": False,
    },
}

# ---------------------------------------------------------------------------
# System Prompt para CAJAL
# ---------------------------------------------------------------------------

P2PCLAW_SYSTEM_PROMPT = (
    "You are CAJAL, an expert AI assistant specialized in peer-to-peer "
    "networks, distributed systems, game theory, mechanism design, and legal-tech "
    "intersections (P2P + CLAW). You provide rigorous, well-cited research assistance, "
    "generate LaTeX-formatted paper drafts, perform mathematical derivations, and "
    "analyze protocol incentives with formal precision. Always think step-by-step and "
    "cite sources when possible."
)

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def print_banner(text: str) -> None:
    width = max(len(text) + 4, 60)
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width + "\n")


def run_cmd(cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    print(f"[CMD] {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def estimate_model_size(base_params: float, size_factor: float, overhead: float = 1.05) -> float:
    """Estima tamaño en GB dado parámetros base (millones) y factor de cuantización."""
    # base_params en millones, FP32 = 4 bytes, factor ya considera reducción vs FP16
    base_size_gb = (base_params * 2.0) / 1024  # FP16 baseline en GB
    return round(base_size_gb * size_factor * overhead, 2)


# ---------------------------------------------------------------------------
# Clases principales
# ---------------------------------------------------------------------------

@dataclass
class ExportConfig:
    model_path: str
    output_dir: str
    quantizations: List[str]
    base_params_billions: float
    ollama_name: str = "cajal"
    context_length: int = 32768
    use_gpu: bool = True
    chat_template: str = "qwen-2.5"
    lora_path: Optional[str] = None
    push_to_hf: Optional[str] = None
    hf_token: Optional[str] = None


class GGUFExporter:
    def __init__(self, config: ExportConfig):
        self.cfg = config
        self.out_dir = Path(config.output_dir).expanduser().resolve()
        self.model_path = Path(config.model_path).expanduser().resolve()
        self.lora_path = Path(config.lora_path).expanduser().resolve() if config.lora_path else None
        self.merged_path: Optional[Path] = None
        self.results: List[Dict] = []

        self.out_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Paso 0: Merge LoRA si es necesario
    # ------------------------------------------------------------------
    def merge_lora_if_needed(self) -> Path:
        if self.lora_path is None or not self.lora_path.exists():
            print("[INFO] No se proporcionó LoRA o no existe. Usando modelo base/ya fusionado.")
            return self.model_path

        print_banner("MERGE LORA ADAPTER")
        merged_dir = self.out_dir / "merged_model"
        merged_dir.mkdir(parents=True, exist_ok=True)

        try:
            from unsloth import FastLanguageModel
        except ImportError:
            print("[ERROR] unsloth no está instalado. Instálalo con: pip install unsloth")
            sys.exit(1)

        print(f"[INFO] Cargando modelo base: {self.model_path}")
        print(f"[INFO] Adaptador LoRA: {self.lora_path}")

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=str(self.model_path),
            max_seq_length=self.cfg.context_length,
            dtype=None,
            load_in_4bit=False,
        )
        model = FastLanguageModel.get_peft_model(model)

        # Cargar pesos LoRA
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, str(self.lora_path))

        print("[INFO] Fusionando pesos LoRA en modelo base...")
        model = model.merge_and_unload()

        print(f"[INFO] Guardando modelo fusionado en: {merged_dir}")
        model.save_pretrained(merged_dir)
        tokenizer.save_pretrained(merged_dir)

        self.merged_path = merged_dir
        return merged_dir

    # ------------------------------------------------------------------
    # Paso 1: Exportar a GGUF vía llama.cpp
    # ------------------------------------------------------------------
    def export_quantization(self, quant_key: str) -> Path:
        info = QUANTIZATION_LEVELS[quant_key]
        quant_method = info["method"]

        merged = self.merged_path or self.model_path
        gguf_out = self.out_dir / f"cajal-{quant_key}.gguf"

        print_banner(f"EXPORTANDO {quant_method}")
        print(f"[INFO] Origen: {merged}")
        print(f"[INFO] Destino: {gguf_out}")

        # Buscar convertidor de llama.cpp
        convert_script = self._find_convert_script()
        if convert_script is None:
            print("[WARN] No se encontró llama.cpp/convert_hf_to_gguf.py")
            print("[INFO] Intentando con llama-cpp-python...")
            self._export_via_llama_cpp_python(merged, gguf_out, quant_key)
            return gguf_out

        # Conversión FP16 primero si no es f16
        fp16_gguf = self.out_dir / "cajal-f16.gguf"
        if not fp16_gguf.exists():
            print("[INFO] Generando GGUF FP16 intermedio...")
            cmd = [
                sys.executable,
                str(convert_script),
                "--outfile", str(fp16_gguf),
                "--outtype", "f16",
                str(merged),
            ]
            run_cmd(cmd)

        if quant_key == "f16":
            return fp16_gguf

        # Quantizar con llama-quantize
        quantize_bin = shutil.which("llama-quantize") or shutil.which("quantize")
        if quantize_bin:
            cmd = [
                quantize_bin,
                str(fp16_gguf),
                str(gguf_out),
                quant_method,
            ]
            run_cmd(cmd)
        else:
            print("[WARN] llama-quantize no encontrado. Usando llama-cpp-python fallback...")
            self._export_via_llama_cpp_python(merged, gguf_out, quant_key)

        return gguf_out

    def _find_convert_script(self) -> Optional[Path]:
        candidates = [
            Path.home() / "llama.cpp" / "convert_hf_to_gguf.py",
            Path.home() / "llama.cpp" / "convert.py",
            Path("/usr/local/bin/convert_hf_to_gguf.py"),
            Path("/opt/llama.cpp/convert_hf_to_gguf.py"),
        ]
        # Buscar también en PATH
        for p in candidates:
            if p.exists():
                return p
        # Buscar en sys.path
        for sp in sys.path:
            candidate = Path(sp) / "llama_cpp" / "convert_hf_to_gguf.py"
            if candidate.exists():
                return candidate
        return None

    def _export_via_llama_cpp_python(self, merged: Path, out: Path, quant_key: str) -> None:
        try:
            from llama_cpp import Llama
        except ImportError:
            print("[ERROR] llama-cpp-python no instalado. pip install llama-cpp-python")
            sys.exit(1)

        # llama-cpp-python no permite cuantizar directamente desde HF fácilmente,
        # así que usamos huggingface_to_gguf vía CLI si existe
        print("[INFO] Conversión alternativa con llama-cpp-python...")
        # Guardamos como FP16 y dejamos que el usuario cuantice manualmente
        # o usamos el convertidor de HuggingFace
        cmd = [
            sys.executable, "-m", "llama_cpp.convert",
            "--outfile", str(out),
            "--outtype", QUANTIZATION_LEVELS[quant_key]["method"].lower(),
            str(merged),
        ]
        try:
            run_cmd(cmd)
        except subprocess.CalledProcessError:
            print("[ERROR] Falló conversión automática. Instale llama.cpp manualmente:")
            print("  git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp && make")
            raise

    # ------------------------------------------------------------------
    # Paso 2: Generar Modelfile para Ollama
    # ------------------------------------------------------------------
    def generate_ollama_modelfile(self) -> Path:
        print_banner("GENERANDE OLLAMA MODELFILE")
        modelfile = self.out_dir / "Modelfile"

        recommended = next((k for k, v in QUANTIZATION_LEVELS.items() if v["recommended"]), "q4_k_m")
        gguf_name = f"cajal-{recommended}.gguf"

        content = f"""# CAJAL Modelfile
# Generado automáticamente por export_to_gguf.py

FROM ./{gguf_name}

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx {self.cfg.context_length}
PARAMETER num_gpu 999

SYSTEM """
{P2PCLAW_SYSTEM_PROMPT}
"""

# Parámetros adicionales para Qwen3 thinking mode
PARAMETER stop <|im_end|>
PARAMETER stop <|endoftext|>
"""

        modelfile.write_text(content, encoding="utf-8")
        print(f"[OK] Modelfile generado: {modelfile}")
        return modelfile

    # ------------------------------------------------------------------
    # Paso 3: Generar config LM Studio
    # ------------------------------------------------------------------
    def generate_lmstudio_config(self) -> Path:
        print_banner("GENERANDO LM STUDIO CONFIG")
        config_path = self.out_dir / "lmstudio_config.json"

        config = {
            "name": self.cfg.ollama_name,
            "architectures": ["Qwen3_5ForConditionalGeneration"],
            "description": "CAJAL: specialized assistant for P2P networks, mechanism design, and legal-tech research.",
            "system_prompt": P2PCLAW_SYSTEM_PROMPT,
            "context_length": self.cfg.context_length,
            "recommended_quantization": "q4_k_m",
            "available_quantizations": [
                {
                    "name": k,
                    "method": v["method"],
                    "quality": v["quality"],
                    "size_factor": v["size_factor"],
                }
                for k, v in QUANTIZATION_LEVELS.items()
            ],
            "inference_settings": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.15,
                "max_tokens": 4096,
            },
            "chat_template": {
                "template": "{% for message in messages %}{% if message['role'] == 'system' %}{{ '<|im_start|>system\\n' + message['content'] + '<|im_end|>\\n' }}{% elif message['role'] == 'user' %}{{ '<|im_start|>user\\n' + message['content'] + '<|im_end|>\\n<|im_start|>assistant\\n' }}{% elif message['role'] == 'assistant' %}{{ message['content'] + '<|im_end|>\\n' }}{% endif %}{% endfor %}",
                "stop_tokens": ["<|im_end|>", "<|endoftext|>"],
            },
            "thinking_mode": {
                "enabled": True,
                "thinking_tag_open": "<|thinking|>",
                "thinking_tag_close": "<|/thinking|>",
            },
        }

        config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] LM Studio config: {config_path}")
        return config_path

    # ------------------------------------------------------------------
    # Paso 4: Tabla comparativa
    # ------------------------------------------------------------------
    def print_comparison_table(self) -> None:
        print_banner("TABLA COMPARATIVA DE CUANTIZACIONES")
        print(f"{'Formato':<12} {'Método':<10} {'Tamaño est.':<14} {'Calidad':<36} {'Recomendado'}")
        print("-" * 85)

        for key, info in QUANTIZATION_LEVELS.items():
            size_gb = estimate_model_size(self.cfg.base_params_billions * 1000, info["size_factor"])
            rec = " <-- RECOMENDADO" if info["recommended"] else ""
            print(f"{key:<12} {info['method']:<10} {size_gb:<8} GB    {info['quality']:<36}{rec}")

        print("\n[NOTA] Los tamaños son estimaciones para FP16 base.\n")

    # ------------------------------------------------------------------
    # Paso 5: Push a Hugging Face (opcional)
    # ------------------------------------------------------------------
    def push_to_huggingface(self) -> None:
        if not self.cfg.push_to_hf:
            return

        print_banner("PUSH A HUGGING FACE HUB")
        try:
            from huggingface_hub import HfApi, create_repo
        except ImportError:
            print("[ERROR] huggingface_hub no instalado. pip install huggingface_hub")
            return

        token = self.cfg.hf_token or os.environ.get("HF_TOKEN")
        if not token:
            print("[ERROR] HF_TOKEN no configurado. Proporcione --hf-token o exporte HF_TOKEN.")
            return

        repo_id = self.cfg.push_to_hf
        api = HfApi(token=token)

        try:
            create_repo(repo_id, exist_ok=True, token=token)
        except Exception as e:
            print(f"[WARN] No se pudo crear repo: {e}")

        print(f"[INFO] Subiendo GGUFs a {repo_id}...")
        for q in self.cfg.quantizations:
            gguf_file = self.out_dir / f"cajal-{q}.gguf"
            if gguf_file.exists():
                api.upload_file(
                    path_or_fileobj=str(gguf_file),
                    path_in_repo=gguf_file.name,
                    repo_id=repo_id,
                    token=token,
                )
                print(f"  [UP] {gguf_file.name}")

        # Subir Modelfile y LM Studio config
        for extra in ["Modelfile", "lmstudio_config.json"]:
            f = self.out_dir / extra
            if f.exists():
                api.upload_file(
                    path_or_fileobj=str(f),
                    path_in_repo=f.name,
                    repo_id=repo_id,
                    token=token,
                )
                print(f"  [UP] {f.name}")

    # ------------------------------------------------------------------
    # Pipeline completo
    # ------------------------------------------------------------------
    def run(self) -> None:
        print_banner("CAJAL GGUF EXPORTER")
        print(f"Modelo origen:  {self.cfg.model_path}")
        print(f"LoRA:           {self.cfg.lora_path or 'N/A'}")
        print(f"Output dir:     {self.out_dir}")
        print(f"Cuantizaciones: {', '.join(self.cfg.quantizations)}")
        print(f"Parámetros:     {self.cfg.base_params_billions}B")

        # Merge LoRA si aplica
        self.merge_lora_if_needed()

        # Mostrar tabla antes de exportar
        self.print_comparison_table()

        # Exportar cada cuantización
        for q in self.cfg.quantizations:
            if q not in QUANTIZATION_LEVELS:
                print(f"[WARN] Cuantización '{q}' no reconocida. Saltando.")
                continue
            self.export_quantization(q)

        # Generar configs
        self.generate_ollama_modelfile()
        self.generate_lmstudio_config()

        # Push a HF opcional
        self.push_to_huggingface()

        print_banner("EXPORT COMPLETADO")
        print(f"[OK] Archivos en: {self.out_dir}")
        print(f"[INFO] Próximos pasos:")
        print(f"  1. cd {self.out_dir}")
        print(f"  2. ollama create cajal -f Modelfile")
        print(f"  3. ollama run cajal")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="export_to_gguf.py",
        description="Exporta modelos CAJAL a GGUF con múltiples cuantizaciones",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Exportar modelo ya fusionado a todas las cuantizaciones
  python export_to_gguf.py --model ./merged_model --params 14

  # Exportar LoRA (auto-merge)
  python export_to_gguf.py --model unsloth/Qwen2.5-14B --lora ./lora_adapter --params 14

  # Solo cuantizaciones específicas
  python export_to_gguf.py --model ./model --params 7 --quants q4_k_m q5_k_m
        """,
    )
    parser.add_argument("--model", required=True, help="Ruta al modelo base o ya fusionado")
    parser.add_argument("--lora", default=None, help="Ruta al adaptador LoRA (opcional)")
    parser.add_argument("--output", default="./gguf_exports", help="Directorio de salida")
    parser.add_argument("--params", type=float, required=True, help="Parámetros del modelo en billones (ej: 7, 14, 32)")
    parser.add_argument(
        "--quants",
        nargs="+",
        choices=list(QUANTIZATION_LEVELS.keys()),
        default=list(QUANTIZATION_LEVELS.keys()),
        help="Niveles de cuantización a generar",
    )
    parser.add_argument("--ollama-name", default="cajal", help="Nombre del modelo en Ollama")
    parser.add_argument("--context-length", type=int, default=32768, help="Longitud de contexto")
    parser.add_argument("--push-to-hf", default=None, help="Repo ID de Hugging Face para subir (ej: user/repo)")
    parser.add_argument("--hf-token", default=None, help="Token de Hugging Face (o env HF_TOKEN)")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = ExportConfig(
        model_path=args.model,
        output_dir=args.output,
        quantizations=args.quants,
        base_params_billions=args.params,
        ollama_name=args.ollama_name,
        context_length=args.context_length,
        lora_path=args.lora,
        push_to_hf=args.push_to_hf,
        hf_token=args.hf_token,
    )
    exporter = GGUFExporter(config)
    exporter.run()


if __name__ == "__main__":
    main()
