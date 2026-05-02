#!/usr/bin/env python3
"""
download_repos_for_cajal.py
===========================
Descarga y procesa ~20 repositorios GitHub de Agnuxo1 para entrenar el modelo CAJAL.

Uso:
    python download_repos_for_cajal.py --all
    python download_repos_for_cajal.py --repos p2pclaw-mcp-server,OpenCLAW-P2P --verbose
    python download_repos_for_cajal.py --all --verbose

Salida:
    ./cajal_repos/<repo>/repo_data.json   # Datos procesados de cada repositorio
    ./cajal_repos/MASTER_INDEX.json       # Índice maestro con estadísticas

Requisitos:
    - Python 3.8+
    - git instalado (opcional: como fallback intenta descarga ZIP via urllib)
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

REPOS: List[str] = [
    "Agnuxo1/p2pclaw-mcp-server",
    "Agnuxo1/p2pclaw-unified",
    "Agnuxo1/OpenCLAW-P2P",
    "Agnuxo1/The-Living-Agent",
    "Agnuxo1/semantic-kernel",
    "Agnuxo1/best-of-lean4",
    "Agnuxo1/EnigmAgent",
    "Agnuxo1/p2pclaw",
    "Agnuxo1/benchclaw",
    "Agnuxo1/CognitionBoard",
    "Agnuxo1/AgentBoot-app",
    "Agnuxo1/AgentBoot",
    "Agnuxo1/pixelflow",
    "Agnuxo1/Project-NAVAJO",
    "Agnuxo1/Token-compression-system-for-improving-agent-cognition",
    "Agnuxo1/King-Skill-Extended-Cognition-Architecture-for-Scientific-LLM-Agents",
    "Agnuxo1/CHIMERA-Chess-Multi-Architecture-Neuromorphic-Engine",
    "Agnuxo1/Universal-Cognitive-Architecture-for-Autonomous-AI-Agents-Text-as-Code-Execution",
    "Agnuxo1/OpenCLAW-Autonomous-Multi-Agent-Scientific-Research-Platform",
]

DEFAULT_WORK_DIR = Path("./cajal_repos")
MAX_FILE_SIZE = 100 * 1024          # 100 KB
MAX_CODE_LINES = 500
MAX_RETRIES = 3
INITIAL_BACKOFF = 2                 # segundos

# Extensiones que SIEMPRE se incluyen (README, docs, etc.)
ALWAYS_INCLUDE_PATTERNS = [
    r"(?i)^readme",
    r"(?i)^contributing\.md$",
    r"(?i)^license",
    r"(?i)^changelog",
    r"(?i)^docs/.*\.md$",
    r"(?i)^src/.*\.md$",
]

# Extensiones de código relevantes
CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".json"}

# Archivos/directorios a EXCLUIR siempre
EXCLUDE_PATTERNS = [
    r"(?i)node_modules",
    r"(?i)\.git",
    r"(?i)^dist$",
    r"(?i)^build$",
    r"(?i)^out$",
    r"(?i)^target$",
    r"(?i)__pycache__",
    r"(?i)\.pytest_cache",
    r"(?i)\.next$",
    r"(?i)\.vercel$",
    r"(?i)^coverage$",
    r"(?i)^\.nuxt$",
    r"(?i)\.lock$",
    r"(?i)\.log$",
    r"(?i)^package-lock\.json$",
    r"(?i)^yarn\.lock$",
    r"(?i)^pnpm-lock\.yaml$",
    r"(?i)^poetry\.lock$",
    r"(?i)^Gemfile\.lock$",
    r"(?i)^composer\.lock$",
    r"(?i)^Cargo\.lock$",
    r"(?i)\.png$", r"(?i)\.jpg$", r"(?i)\.jpeg$", r"(?i)\.gif$",
    r"(?i)\.svg$", r"(?i)\.ico$", r"(?i)\.bmp$", r"(?i)\.webp$",
    r"(?i)\.mp4$", r"(?i)\.avi$", r"(?i)\.mov$", r"(?i)\.mkv$",
    r"(?i)\.mp3$", r"(?i)\.wav$", r"(?i)\.ogg$",
    r"(?i)\.exe$", r"(?i)\.dll$", r"(?i)\.so$", r"(?i)\.dylib$",
    r"(?i)\.zip$", r"(?i)\.tar$", r"(?i)\.gz$", r"(?i)\.rar$",
    r"(?i)\.7z$", r"(?i)\.bz2$",
    r"(?i)\.woff$", r"(?i)\.woff2$", r"(?i)\.ttf$", r"(?i)\.eot$",
    r"(?i)\.pdf$", r"(?i)\.docx$", r"(?i)\.xlsx$",
    r"(?i)^\.gitignore$", r"(?i)^\.gitattributes$",
    r"(?i)^\.editorconfig$", r"(?i)^\.prettierrc",
    r"(?i)^\.eslintrc", r"(?i)^\.stylelintrc",
    r"(?i)^\.dockerignore$", r"(?i)^Dockerfile$",
    r"(?i)^\.github$", r"(?i)^\.vscode$", r"(?i)^\.idea$",
]

# =============================================================================
# UTILIDADES
# =============================================================================

def log(msg: str, verbose: bool, level: str = "INFO") -> None:
    """Imprime mensaje si verbose es True o si es WARNING/ERROR."""
    if verbose or level in ("WARNING", "ERROR"):
        print(f"[{level}] {msg}", file=sys.stderr if level == "ERROR" else sys.stdout)


def should_exclude(rel_path: str, file_name: str) -> bool:
    """Determina si un archivo debe excluirse basado en patrones."""
    full = rel_path.replace("\\", "/")
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, full) or re.search(pat, file_name):
            return True
    return False


def should_always_include(rel_path: str, file_name: str) -> bool:
    """Determina si un archivo SIEMPRE debe incluirse (README, docs, etc.)."""
    full = rel_path.replace("\\", "/")
    for pat in ALWAYS_INCLUDE_PATTERNS:
        if re.search(pat, full) or re.search(pat, file_name):
            return True
    return False


def is_code_file(file_name: str) -> bool:
    """Verifica si la extensión es de código relevante."""
    return any(file_name.lower().endswith(ext) for ext in CODE_EXTENSIONS)


def count_lines(text: str) -> int:
    """Cuenta líneas de texto."""
    return len(text.splitlines())


def run_cmd(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 120) -> Tuple[int, str, str]:
    """Ejecuta comando y retorna (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout exceeded"
    except FileNotFoundError:
        return -2, "", f"Command not found: {cmd[0]}"


def git_available() -> bool:
    """Verifica si git está instalado."""
    rc, _, _ = run_cmd(["git", "--version"])
    return rc == 0


def download_zip_fallback(repo_full: str, dest: Path, verbose: bool) -> bool:
    """Descarga ZIP de GitHub como fallback si git no está disponible."""
    url = f"https://github.com/{repo_full}/archive/refs/heads/main.zip"
    zip_path = dest / "repo.zip"
    try:
        log(f"Descargando ZIP fallback: {url}", verbose)
        urllib.request.urlretrieve(url, str(zip_path))
        shutil.unpack_archive(str(zip_path), str(dest))
        # GitHub ZIP extrae en <repo>-main/
        extracted = list(dest.iterdir())
        for item in extracted:
            if item.is_dir() and item.name.endswith("-main"):
                # Mover contenido a destino base
                for sub in item.iterdir():
                    shutil.move(str(sub), str(dest / sub.name))
                shutil.rmtree(str(item))
                break
        zip_path.unlink(missing_ok=True)
        return True
    except Exception as e:
        log(f"ZIP fallback falló para {repo_full}: {e}", verbose, "WARNING")
        return False


def clone_or_pull(repo_full: str, dest: Path, verbose: bool) -> Tuple[bool, str]:
    """Clona o actualiza un repositorio. Retorna (exito, mensaje)."""
    url = f"https://github.com/{repo_full}.git"
    repo_name = repo_full.split("/")[1]
    repo_dir = dest / repo_name

    if not git_available():
        log("Git no encontrado. Usando descarga ZIP como fallback.", verbose, "WARNING")
        ok = download_zip_fallback(repo_full, dest, verbose)
        return ok, "ZIP fallback" if ok else "ZIP fallback failed"

    if repo_dir.exists() and (repo_dir / ".git").exists():
        log(f"Repo {repo_name} ya existe. Haciendo pull...", verbose)
        for attempt in range(MAX_RETRIES):
            rc, out, err = run_cmd(["git", "pull", "--depth=1"], cwd=repo_dir)
            if rc == 0:
                return True, "updated"
            log(f"Pull falló (intento {attempt + 1}): {err}", verbose, "WARNING")
            time.sleep(INITIAL_BACKOFF * (2 ** attempt))
        return False, f"git pull failed after {MAX_RETRIES} retries"
    else:
        log(f"Clonando {repo_full} ...", verbose)
        for attempt in range(MAX_RETRIES):
            rc, out, err = run_cmd(
                ["git", "clone", "--depth", "1", url, str(repo_dir)],
                cwd=dest,
                timeout=180,
            )
            if rc == 0:
                return True, "cloned"
            log(f"Clone falló (intento {attempt + 1}): {err}", verbose, "WARNING")
            time.sleep(INITIAL_BACKOFF * (2 ** attempt))
        return False, f"git clone failed after {MAX_RETRIES} retries"


def extract_repo_info(repo_dir: Path) -> Tuple[str, str]:
    """Extrae descripción desde README o git remote."""
    description = ""
    readme_candidates = list(repo_dir.glob("README*")) + list(repo_dir.glob("readme*"))
    for readme in readme_candidates:
        if readme.is_file():
            try:
                text = readme.read_text(encoding="utf-8", errors="replace")
                # Primera línea no vacía como descripción
                for line in text.splitlines()[:10]:
                    stripped = line.strip().lstrip("# ").strip()
                    if stripped:
                        description = stripped
                        break
                break
            except Exception:
                pass
    if not description:
        description = "No description available"
    return description


def get_directory_tree(repo_dir: Path, max_depth: int = 3) -> str:
    """Genera árbol de directorios con profundidad limitada."""
    lines: List[str] = []
    prefix = ""

    def walk(current: Path, depth: int, prefix: str) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(
                [e for e in current.iterdir() if not e.name.startswith(".")],
                key=lambda e: (e.is_file(), e.name.lower()),
            )
        except PermissionError:
            return
        for i, entry in enumerate(entries):
            if should_exclude(str(entry.relative_to(repo_dir)), entry.name):
                continue
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                walk(entry, depth + 1, prefix + extension)

    walk(repo_dir, 0, "")
    return "\n".join(lines)


def extract_repo_data(repo_full: str, repo_dir: Path, verbose: bool) -> Dict[str, Any]:
    """Extrae y estructura contenido relevante de un repositorio."""
    owner, repo_name = repo_full.split("/")
    description = extract_repo_info(repo_dir)

    readme_content = ""
    docs_files: List[Dict[str, str]] = []
    key_files: List[Dict[str, str]] = []
    total_lines = 0
    total_bytes = 0
    processed_count = 0

    for root, _dirs, files in os.walk(repo_dir):
        root_path = Path(root)
        for fname in files:
            fpath = root_path / fname
            rel = str(fpath.relative_to(repo_dir)).replace("\\", "/")

            if should_exclude(rel, fname):
                continue

            # Tamaño
            try:
                fsize = fpath.stat().st_size
            except OSError:
                continue
            if fsize > MAX_FILE_SIZE:
                continue

            # Leer contenido
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            f_lines = count_lines(content)

            # Siempre incluir READMEs y docs
            if should_always_include(rel, fname):
                if re.search(r"(?i)^readme", fname):
                    readme_content = content
                else:
                    docs_files.append({"file": rel, "content": content})
                total_lines += f_lines
                total_bytes += fsize
                processed_count += 1
                continue

            # Código relevante con límites
            if is_code_file(fname):
                if f_lines > MAX_CODE_LINES:
                    log(f"  Skip {rel} ({f_lines} líneas > {MAX_CODE_LINES})", verbose)
                    continue
                key_files.append({"file": rel, "content": content})
                total_lines += f_lines
                total_bytes += fsize
                processed_count += 1

    # Construir salida
    data = {
        "repo_name": repo_name,
        "repo_url": f"https://github.com/{repo_full}",
        "owner": owner,
        "description": description,
        "content": {
            "readme": readme_content,
            "docs": docs_files,
            "key_files": key_files,
            "structure": get_directory_tree(repo_dir),
        },
        "stats": {
            "files_processed": processed_count,
            "lines_extracted": total_lines,
            "bytes_extracted": total_bytes,
        },
    }
    return data


def save_repo_json(repo_data: Dict[str, Any], dest: Path) -> Path:
    """Guarda datos de repositorio como JSON."""
    repo_name = repo_data["repo_name"]
    out_dir = dest / repo_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "repo_data.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(repo_data, f, indent=2, ensure_ascii=False)
    return out_file


def build_master_index(all_results: List[Dict[str, Any]], dest: Path) -> Path:
    """Genera MASTER_INDEX.json con resumen global."""
    total_files = sum(r.get("stats", {}).get("files_processed", 0) for r in all_results)
    total_lines = sum(r.get("stats", {}).get("lines_extracted", 0) for r in all_results)
    total_bytes = sum(r.get("stats", {}).get("bytes_extracted", 0) for r in all_results)

    index = {
        "project": "CAJAL Dataset",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_repos": len(all_results),
        "summary": {
            "total_files_processed": total_files,
            "total_lines_extracted": total_lines,
            "total_bytes_extracted": total_bytes,
        },
        "repositories": [
            {
                "repo_name": r["repo_name"],
                "repo_url": r["repo_url"],
                "description": r["description"],
                "files_processed": r.get("stats", {}).get("files_processed", 0),
                "lines_extracted": r.get("stats", {}).get("lines_extracted", 0),
                "bytes_extracted": r.get("stats", {}).get("bytes_extracted", 0),
            }
            for r in all_results
        ],
    }

    out_file = dest / "MASTER_INDEX.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    return out_file


def print_report(results: List[Dict[str, Any]], statuses: Dict[str, str], verbose: bool) -> None:
    """Imprime tabla resumen final."""
    print("\n" + "=" * 90)
    print(f"{'REPO':<45} {'ESTADO':<10} {'FILES':<8} {'LÍNEAS':<10} {'TAMAÑO':<12}")
    print("=" * 90)
    for r in results:
        name = r["repo_name"]
        status = statuses.get(name, "UNKNOWN")
        stats = r.get("stats", {})
        files = stats.get("files_processed", 0)
        lines = stats.get("lines_extracted", 0)
        bts = stats.get("bytes_extracted", 0)
        size_str = f"{bts / 1024:.1f} KB" if bts < 1024 * 1024 else f"{bts / (1024 * 1024):.2f} MB"
        print(f"{name:<45} {status:<10} {files:<8} {lines:<10} {size_str:<12}")
    print("=" * 90)

    total_repos = len(results)
    ok_count = sum(1 for s in statuses.values() if s == "OK")
    err_count = sum(1 for s in statuses.values() if s == "ERROR")
    skip_count = sum(1 for s in statuses.values() if s == "SKIP")
    total_files = sum(r.get("stats", {}).get("files_processed", 0) for r in results)
    total_lines = sum(r.get("stats", {}).get("lines_extracted", 0) for r in results)
    total_bytes = sum(r.get("stats", {}).get("bytes_extracted", 0) for r in results)

    print(f"\nResumen: {ok_count} OK, {err_count} ERROR, {skip_count} SKIP  |  "
          f"{total_files} archivos, {total_lines:,} líneas, {total_bytes / 1024:.1f} KB total")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Descarga y procesa repositorios GitHub para el dataset CAJAL",
    )
    parser.add_argument("--all", action="store_true", help="Procesar todos los repositorios")
    parser.add_argument(
        "--repos",
        type=str,
        default="",
        help="Lista separada por comas de nombres de repo (ej: p2pclaw-mcp-server,OpenCLAW-P2P)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
    parser.add_argument(
        "--work-dir",
        type=str,
        default=str(DEFAULT_WORK_DIR),
        help=f"Directorio de trabajo (default: {DEFAULT_WORK_DIR})",
    )
    args = parser.parse_args()

    if not args.all and not args.repos:
        parser.print_help()
        print("\nError: Debes especificar --all o --repos", file=sys.stderr)
        return 1

    work_dir = Path(args.work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    # Seleccionar repositorios a procesar
    if args.all:
        selected = REPOS[:]
    else:
        names = {n.strip() for n in args.repos.split(",") if n.strip()}
        selected = [r for r in REPOS if r.split("/")[1] in names]
        missing = names - {r.split("/")[1] for r in selected}
        if missing:
            log(f"Repos no encontrados en la lista: {', '.join(missing)}", args.verbose, "WARNING")

    log(f"Directorio de trabajo: {work_dir}", args.verbose)
    log(f"Repositorios a procesar: {len(selected)}", args.verbose)

    results: List[Dict[str, Any]] = []
    statuses: Dict[str, str] = {}

    for repo_full in selected:
        repo_name = repo_full.split("/")[1]
        log(f"\n>>> Procesando {repo_full} ...", args.verbose)

        # 1. Clonar / actualizar
        ok, msg = clone_or_pull(repo_full, work_dir, args.verbose)
        if not ok:
            log(f"No se pudo obtener {repo_full}: {msg}", args.verbose, "ERROR")
            statuses[repo_name] = "ERROR"
            results.append({
                "repo_name": repo_name,
                "repo_url": f"https://github.com/{repo_full}",
                "owner": repo_full.split("/")[0],
                "description": f"ERROR: {msg}",
                "content": {},
                "stats": {"files_processed": 0, "lines_extracted": 0, "bytes_extracted": 0},
            })
            continue

        repo_dir = work_dir / repo_name
        if not repo_dir.exists():
            log(f"Directorio no encontrado tras clone: {repo_dir}", args.verbose, "ERROR")
            statuses[repo_name] = "ERROR"
            continue

        # 2. Extraer datos
        try:
            data = extract_repo_data(repo_full, repo_dir, args.verbose)
        except Exception as e:
            log(f"Error extrayendo {repo_full}: {e}", args.verbose, "ERROR")
            statuses[repo_name] = "ERROR"
            continue

        # 3. Guardar JSON
        try:
            save_repo_json(data, work_dir)
            log(f"  Guardado en {work_dir / repo_name / 'repo_data.json'}", args.verbose)
        except Exception as e:
            log(f"Error guardando JSON para {repo_full}: {e}", args.verbose, "ERROR")
            statuses[repo_name] = "ERROR"
            continue

        results.append(data)
        statuses[repo_name] = "OK"

    # 4. Master index
    if results:
        try:
            idx_path = build_master_index(results, work_dir)
            log(f"\nMaster index guardado en: {idx_path}", args.verbose)
        except Exception as e:
            log(f"Error generando MASTER_INDEX: {e}", args.verbose, "ERROR")

    # 5. Reporte
    print_report(results, statuses, args.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
