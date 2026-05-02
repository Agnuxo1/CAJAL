#!/usr/bin/env python3
"""
download_from_api.py

Descarga el dataset de P2PCLAW directamente desde su API pública
y lo guarda en formato JSONL (una lnea JSON por registro),
compatible con frameworks de fine-tuning como Unsloth, Axolotl,
LLaMA-Factory, etc.

URL base: https://www.p2pclaw.com/api/dataset/export

Uso:
    python download_from_api.py
    python download_from_api.py --min_score 0.5 --fields title,content,granular_scores
    python download_from_api.py --output mi_dataset.jsonl --format jsonl

Dependencias:
    pip install requests tqdm

Autor: CAJAL Dataset Agent
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIN POR DEFECTO
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_BASE_URL = "https://www.p2pclaw.com"
DEFAULT_ENDPOINT = "/api/dataset/export"
DEFAULT_OUTPUT   = "p2pclaw_dataset.jsonl"
DEFAULT_MIN_SCORE = 0
DEFAULT_FIELDS    = "title,content,granular_scores,lean_verified"
DEFAULT_FORMAT    = "jsonl"      # jsonl | json  (la API puede devolver ambos)
DEFAULT_TIMEOUT   = 120          # segundos
CHUNK_SIZE        = 8192         # bytes para descarga en streaming


# ═══════════════════════════════════════════════════════════════════════════════
# SESIN HTTP CON RETRY ROBUSTO
# ═══════════════════════════════════════════════════════════════════════════════

def create_session(max_retries: int = 3) -> requests.Session:
    """
    Crea una sesin requests con backoff exponencial para reintentos
    automticos ante errores transitorios de red (503, 502, 504, etc.).
    """
    session = requests.Session()
    retries = Retry(
        total=max_retries,
        backoff_factor=1.0,          # espera 1s, 2s, 4s entre reintentos
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


# ═══════════════════════════════════════════════════════════════════════════════
# BARRA DE PROGRESO MANUAL (sin tqdm si no est disponible)
# ═══════════════════════════════════════════════════════════════════════════════

def print_progress(downloaded: int, total: int | None, start_time: datetime):
    """Imprime progreso de descarga en la misma lnea de consola."""
    elapsed = (datetime.now() - start_time).total_seconds()
    if total and total > 0:
        pct = downloaded / total * 100
        mb_d = downloaded / (1024 * 1024)
        mb_t = total / (1024 * 1024)
        speed = mb_d / elapsed if elapsed > 0 else 0
        bar_len = 30
        filled = int(bar_len * downloaded / total)
        bar = "=" * filled + ">" + "." * (bar_len - filled - 1)
        sys.stdout.write(
            f"\r   [{bar}] {pct:5.1f}%  {mb_d:6.2f}/{mb_t:6.2f} MB  {speed:5.2f} MB/s"
        )
    else:
        mb_d = downloaded / (1024 * 1024)
        speed = mb_d / elapsed if elapsed > 0 else 0
        sys.stdout.write(f"\r   Descargado: {mb_d:6.2f} MB  {speed:5.2f} MB/s  (tamao desconocido)")
    sys.stdout.flush()


# ═══════════════════════════════════════════════════════════════════════════════
# DESCARGA DESDE LA API
# ═══════════════════════════════════════════════════════════════════════════════

def download_dataset(
    session: requests.Session,
    base_url: str,
    endpoint: str,
    min_score: float,
    fields: str,
    fmt: str,
    output_path: Path,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """
    Realiza la peticin GET a la API de P2PCLAW y guarda la respuesta.

    Args:
        session:     Sesin requests configurada con retries.
        base_url:    URL base del servidor P2PCLAW.
        endpoint:    Ruta del endpoint de exportacin.
        min_score:   Puntuacin mnima de los papers a incluir.
        fields:      Campos a incluir, separados por comas.
        fmt:         Formato de salida solicitado a la API.
        output_path: Ruta local donde se escribir el archivo.
        timeout:     Timeout en segundos para la peticin.

    Returns:
        Diccionario con {success: bool, records: int, path: str, error: str|None}
    """
    query = {
        "min_score": min_score,
        "fields": fields,
        "format": fmt,
    }
    url = f"{base_url.rstrip('/')}{endpoint}?{urlencode(query)}"

    print(f"\n[1/4] Endpoint: {url}")
    print(f"[2/4] Destino : {output_path.absolute()}")
    print("[3/4] Iniciando descarga ...")

    try:
        response = session.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return {"success": False, "records": 0, "path": str(output_path), "error": "Timeout de conexin"}
    except requests.exceptions.ConnectionError as exc:
        return {"success": False, "records": 0, "path": str(output_path), "error": f"Error de conexin: {exc}"}
    except requests.exceptions.HTTPError as exc:
        return {"success": False, "records": 0, "path": str(output_path), "error": f"HTTP {exc.response.status_code}: {exc}"}

    # Obtener tamao total si el servidor lo indica
    total_length = response.headers.get("Content-Length")
    total_bytes = int(total_length) if total_length and total_length.isdigit() else None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    start_time = datetime.now()
    downloaded = 0
    records = 0

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                print_progress(downloaded, total_bytes, start_time)

    sys.stdout.write("\n")

    # Si la API devuelve JSONL, contamos registros (lneas)
    if fmt.lower() == "jsonl" or output_path.suffix.lower() == ".jsonl":
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                records = sum(1 for _ in f)
        except Exception:
            records = -1  # no se pudo contar

    elapsed = (datetime.now() - start_time).total_seconds()
    size_mb = output_path.stat().st_size / (1024 * 1024)

    print(f"[4/4] Completado en {elapsed:.1f}s | {size_mb:.2f} MB | {records} registros")
    return {"success": True, "records": records, "path": str(output_path), "error": None}


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDACIN / SANITY CHECK DEL DATASET DESCARGADO
# ═══════════════════════════════════════════════════════════════════════════════

def validate_jsonl(path: Path, max_lines: int = 10) -> dict:
    """
    Valida las primeras lneas del archivo JSONL descargado.

    Comprueba:
      - Que cada lnea sea JSON vlido.
      - Presencia de campos esperados (title, content, lean_verified).
      - Estructura de 'messages' si es un dataset de chat.

    Retorna resumen con {valid_lines, errors, sample_fields}.
    """
    print("\n[Validacin] Analizando estructura del dataset ...")

    valid_lines = 0
    errors = []
    sample_fields = set()
    sample_messages_structure = None

    try:
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= max_lines * 5:          # analizamos hasta 50 lneas para estadsticas
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    valid_lines += 1
                    sample_fields.update(obj.keys())

                    # Detectar estructura de conversacin/chat (Qwen3, Gemma4, etc.)
                    if "messages" in obj and isinstance(obj["messages"], list):
                        if sample_messages_structure is None:
                            roles = [m.get("role", "?") for m in obj["messages"]]
                            sample_messages_structure = roles
                except json.JSONDecodeError as exc:
                    if len(errors) < 5:
                        errors.append(f"Lnea {i+1}: {exc}")
    except Exception as exc:
        return {"valid_lines": 0, "errors": [str(exc)], "sample_fields": set(), "messages_roles": None}

    print(f"       Lneas JSON vlidas analizadas: {valid_lines}")
    print(f"       Campos detectados: {', '.join(sorted(sample_fields)) or '(ninguno)'}")
    if sample_messages_structure:
        print(f"       Estructura 'messages' detectada: {sample_messages_structure}")
        print("       -> Compatible con formato de conversacin (Qwen3, Gemma4, etc.)")
    else:
        print("       -> No se detect estructura 'messages'. Puede ser un JSON plano de papers.")

    if errors:
        print(f"       Errores de parsing (primeros {len(errors)}):")
        for e in errors:
            print(f"         ! {e}")

    return {
        "valid_lines": valid_lines,
        "errors": errors,
        "sample_fields": sample_fields,
        "messages_roles": sample_messages_structure,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVERSIN A FORMATO CHAT ESTNDAR (OPCIONAL)
# ═══════════════════════════════════════════════════════════════════════════════

def convert_to_chat_format(input_path: Path, output_path: Path) -> dict:
    """
    Si el JSONL de entrada NO tiene formato de conversacin (campo 'messages'),
    intenta convertirlo a un JSONL estndar con el campo 'messages' usando
    los campos 'title' y 'content' como mensajes de usuario y asistente.

    Esto es til para adaptar datasets de papers al formato que esperan
    Qwen3, Gemma 4, etc.:
        { "messages": [
            {"role": "user",      "content": "Resumen de: <title>"},
            {"role": "assistant", "content": "<content>"}
        ]}

    Retorna {converted, output_path, records}.
    """
    print(f"\n[Conversin] Adaptando a formato chat estndar ...")
    print(f"       Origen:  {input_path}")
    print(f"       Destino: {output_path}")

    converted = 0
    skipped = 0
    errors = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)

                # Ya tiene formato chat -> copiar tal cual
                if "messages" in obj and isinstance(obj["messages"], list):
                    fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                    skipped += 1
                    continue

                # Convertir desde formato plano de papers
                title   = obj.get("title", "")
                content = obj.get("content", "")
                lean    = obj.get("lean_verified", None)
                scores  = obj.get("granular_scores", {})

                system_msg = (
                    "You are CAJAL, an AI scientist in the P2PCLAW decentralized "
                    "research network. You write rigorous, reproducible academic "
                    "papers with structured methodology, statistical analysis, "
                    "Lean 4 proofs, and proper citations."
                )

                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"Proporciona un anlisis del siguiente paper: {title}"},
                    {"role": "assistant", "content": content},
                ]

                # Incluir metadatos extra si existen
                extra = {}
                if lean is not None:
                    extra["lean_verified"] = lean
                if scores:
                    extra["granular_scores"] = scores

                chat_obj = {"messages": messages}
                if extra:
                    chat_obj["metadata"] = extra

                fout.write(json.dumps(chat_obj, ensure_ascii=False) + "\n")
                converted += 1

            except Exception as exc:
                errors += 1
                if errors <= 3:
                    print(f"       Error conversin lnea: {exc}")

    print(f"       Convertidos: {converted} | Ya en formato chat: {skipped} | Errores: {errors}")
    return {"converted": converted, "output_path": str(output_path), "records": converted + skipped}


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Descarga el dataset de P2PCLAW desde su API pblica."
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"URL base del servidor P2PCLAW (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help=f"Ruta del endpoint de exportacin (default: {DEFAULT_ENDPOINT})",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=DEFAULT_MIN_SCORE,
        help=f"Puntuacin mnima de papers a incluir (default: {DEFAULT_MIN_SCORE})",
    )
    parser.add_argument(
        "--fields",
        default=DEFAULT_FIELDS,
        help=f"Campos a exportar, separados por comas (default: {DEFAULT_FIELDS})",
    )
    parser.add_argument(
        "--format",
        choices=["json", "jsonl"],
        default=DEFAULT_FORMAT,
        help=f"Formato de salida (default: {DEFAULT_FORMAT})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Ruta del archivo de salida (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout de la peticin en segundos (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--convert-chat",
        action="store_true",
        help="Convierte automticamente a formato de conversacin ('messages') si aplica.",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Omitir la validacin post-descarga.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Nmero de reintentos ante fallos de red (default: 3)",
    )

    args = parser.parse_args()

    print("=" * 72)
    print("   CAJAL DATASET DOWNLOADER  |  API Export Client")
    print("=" * 72)
    print(f"   Base URL : {args.base_url}")
    print(f"   Endpoint : {args.endpoint}")
    print(f"   Params   : min_score={args.min_score}, fields={args.fields}, format={args.format}")

    output_path = Path(args.output)

    session = create_session(max_retries=args.retries)
    result = download_dataset(
        session=session,
        base_url=args.base_url,
        endpoint=args.endpoint,
        min_score=args.min_score,
        fields=args.fields,
        fmt=args.format,
        output_path=output_path,
        timeout=args.timeout,
    )

    if not result["success"]:
        print(f"\n[!] FALLA: {result['error']}")
        sys.exit(1)

    # Validacin
    if not args.no_validate:
        validate_jsonl(output_path, max_lines=10)

    # Conversin opcional a formato chat
    if args.convert_chat:
        chat_output = output_path.with_suffix(".chat.jsonl")
        convert_to_chat_format(output_path, chat_output)
        print(f"\n[OK] Archivo final listo para entrenamiento: {chat_output}")
    else:
        print(f"\n[OK] Archivo descargado correctamente: {output_path}")

    print("\n" + "=" * 72)
    print("   PRXIMOS PASOS:")
    print("=" * 72)
    print("""
   1. Revisa el contenido con: head -n 5 <archivo>.jsonl
   2. Valida que cada lnea tenga JSON vlido.
   3. Si usas Unsloth / Axolotl, asegura el campo 'messages' con roles.
   4. Entrena con:
      from datasets import load_dataset
      ds = load_dataset("json", data_files="<archivo>.jsonl")
""")


if __name__ == "__main__":
    main()
