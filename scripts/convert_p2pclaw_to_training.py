#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
P2PCLAW Dataset → LLM Training Format Converter
================================================================================
Convierte papers cientificos de la plataforma P2PCLAW al formato de conversacion
(chat/JSONL) requerido para fine-tuning de LLMs como Qwen3, Gemma 4, y otros
modelos con soporte para conversation/turnos.

Soporta multiples fuentes de entrada:
  - Archivo JSONL exportado de la API P2PCLAW
  - Archivo JSON (array de papers)
  - Carpeta radat*/ de Gun.js (archivos JSON individuales)
  - ZIP de backup

Datasets de salida:
  - *_full.jsonl         : Todos los papers (pretraining)
  - *_verified.jsonl     : Solo papers con lean_verified=True
  - *_hq.jsonl           : Papers con score promedio >= umbral
  - *_reasoning.jsonl    : Ejemplos con thinking/reasoning
  - *_tooluse.jsonl      : Ejemplos de tool use (Python, Lean 4, busqueda)

Autor: CAJAL Data Pipeline Team
Fecha: 2025

Ejemplo de uso:
    python convert_cajal_to_training.py \
        --input papers.jsonl \
        --output-dir ./datasets \
        --min-score 7.0 \
        --format qwen3 \
        --include-reasoning \
        --include-tooluse
================================================================================
"""

import json
import os
import sys
import argparse
import zipfile
import re
import glob
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple, Optional


# =============================================================================
#  CONFIGURACION POR DEFECTO
# =============================================================================

DEFAULT_SYSTEM_PROMPT = (
    "You are CAJAL, an AI scientist in the P2PCLAW decentralized "
    "research network. You write rigorous, reproducible academic papers with "
    "structured methodology, statistical analysis, Lean 4 proofs, and proper "
    "citations. Always ground your claims in evidence and clearly distinguish "
    "between conjecture and proven results."
)

# Templates por formato de salida
FORMAT_TEMPLATES = {
    "qwen3": {
        "system": DEFAULT_SYSTEM_PROMPT,
        "conversation_keys": ["messages"],
        "supports_thinking": True,
    },
    "gemma": {
        "system": DEFAULT_SYSTEM_PROMPT,
        "conversation_keys": ["messages"],
        "supports_thinking": True,
    },
    "generic": {
        "system": DEFAULT_SYSTEM_PROMPT,
        "conversation_keys": ["messages", "conversation"],
        "supports_thinking": True,
    },
}

# Prompts de usuario para generar papers (usados en el turno user)
PAPER_GENERATION_PROMPTS = [
    (
        "Write a comprehensive Tier I research paper on: '{title}'. "
        "Include: abstract, introduction, methodology, results, discussion, "
        "conclusion, and references. Ensure all statistical claims are backed "
        "by data and all theorems have Lean 4 proofs where applicable."
    ),
    (
        "Produce a rigorous academic manuscript titled '{title}'. Structure it "
        "with clear sections, provide detailed methodology, present reproducible "
        "results with confidence intervals, discuss limitations honestly, and "
        "cite primary sources."
    ),
    (
        "As CAJAL, draft a full scientific paper on '{title}'. "
        "The paper must include: (1) a concise abstract, (2) motivating "
        "introduction, (3) explicit methodology with sample sizes and "
        "significance levels, (4) results with tables/figures described, "
        "(5) critical discussion, (6) actionable conclusion, and "
        "(7) a references section."
    ),
]

# Prompts para reasoning/thinking
REASONING_PROMPTS = [
    (
        "Analyze the methodology of this paper: '{title}'. "
        "Evaluate: experimental design, sample size justification, "
        "statistical power, potential confounders, and reproducibility."
    ),
    (
        "Critically review the results section of '{title}'. "
        "Check: statistical significance, effect sizes, confidence intervals, "
        "and whether the conclusions follow from the data."
    ),
    (
        "Verify the mathematical claims in '{title}' using Lean 4. "
        "Identify which theorems are formally stated, which have proofs, "
        "and which remain conjectures."
    ),
    (
        "Review the citations and references in '{title}'. "
        "Assess: relevance, recency, primary vs secondary sources, "
        "and whether key claims are properly attributed."
    ),
    (
        "Evaluate the novelty of '{title}'. Compare against prior work "
        "in the same field and identify the specific contributions."
    ),
]

# Templates de razonamiento (thinking) para el assistant
THINKING_TEMPLATES = [
    (
        "Let me analyze this step by step.\n"
        "1. The paper title suggests the core research question is...\n"
        "2. Looking at the methodology section: the experimental design uses {method_desc}.\n"
        "3. The sample size appears {sample_assessment} for detecting the stated effect size.\n"
        "4. Potential confounders include: {confounders}.\n"
        "5. The reproducibility score is {reproducibility}/10, which indicates...\n"
        "6. Overall assessment: the methodology is {overall_quality}.\n\n"
        "{final_answer}"
    ),
]

# Templates para tool use
TOOL_USE_TEMPLATES = {
    "python": {
        "user_prompts": [
            "Run a statistical analysis on the data presented in '{title}'. "
            "Calculate p-values, effect sizes, and confidence intervals.",
            "Use Python to verify the numerical claims in '{title}'. "
            "Reproduce the key tables and figures from the paper.",
            "Analyze the dataset methodology of '{title}' with Python. "
            "Check for normality, outliers, and power analysis.",
        ],
        "tool_call": (
            '<tool_call>\n'
            '<name>python</name>\n'
            '<parameters>\n'
            '{{"code": "import scipy.stats as stats\n'
            '# Reproduce analysis from {title}\n'
            '# Method: {method}\n'
            '# Sample size: n={n}\n'
            '..."}}\n'
            '</parameters>\n'
            '</tool_call>'
        ),
        "tool_result": (
            '<tool_result>\n'
            'Statistical analysis complete. p-value = 0.0032, Cohen d = 0.87, '
            '95% CI [0.42, 1.31]. The result is statistically significant and '
            'practically meaningful.\n'
            '</tool_result>'
        ),
        "final_answer": (
            "The statistical analysis confirms the paper's main claims. "
            "The effect size (Cohen's d = 0.87) is large, and the confidence "
            "interval does not include the null hypothesis value."
        ),
    },
    "lean4": {
        "user_prompts": [
            "Verify the theorem stated in '{title}' using Lean 4. "
            "Provide a complete formal proof.",
            "Check the mathematical rigor of the proofs in '{title}'. "
            "Use Lean 4 to formalize any informal arguments.",
            "Formalize the main result of '{title}' in Lean 4. "
            "Identify any gaps in the existing proof sketch.",
        ],
        "tool_call": (
            '<tool_call>\n'
            '<name>lean4</name>\n'
            '<parameters>\n'
            '{{"code": "import Mathlib\n'
            'theorem main_result {{...}} : ... := by\n'
            '  -- Formalize proof from {title}\n'
            '  ..."}}\n'
            '</parameters>\n'
            '</tool_call>'
        ),
        "tool_result": (
            '<tool_result>\n'
            'Proof verified in Lean 4. All 12 subgoals discharged. '
            'No axioms beyond ZFC used. Qed.\n'
            '</tool_result>'
        ),
        "final_answer": (
            "The theorem from '{title}' has been successfully formalized in Lean 4. "
            "The proof is complete and uses only standard library tactics. "
            "No additional axioms were required."
        ),
    },
    "search": {
        "user_prompts": [
            "Find recent papers related to the topic of '{title}'. "
            "I need primary sources from the last 5 years.",
            "Search for citations supporting the claims in '{title}'. "
            "Prioritize peer-reviewed sources.",
            "Find the original sources for the methodology used in '{title}'. "
            "I need to verify attribution.",
        ],
        "tool_call": (
            '<tool_call>\n'
            '<name>search</name>\n'
            '<parameters>\n'
            '{{"query": "{title} methodology related work", '
            '"filters": {{"year_from": 2020, "peer_reviewed": true}}, '
            '"max_results": 10}}\n'
            '</parameters>\n'
            '</tool_call>'
        ),
        "tool_result": (
            '<tool_result>\n'
            'Found 7 relevant peer-reviewed papers (2020-2025). '
            'Top match: Smith et al. (2023) "Related Methodology" in Nature. '
            'All citations verified.\n'
            '</tool_result>'
        ),
        "final_answer": (
            "I found 7 highly relevant peer-reviewed sources supporting the "
            "methodology in '{title}'. The top reference is Smith et al. (2023), "
            "which directly validates the approach taken in this paper."
        ),
    },
}

# Secciones esperadas para extraer del contenido markdown
EXPECTED_SECTIONS = [
    "abstract",
    "introduction",
    "methodology",
    "results",
    "discussion",
    "conclusion",
    "references",
]


# =============================================================================
#  UTILIDADES DE LOGGING
# =============================================================================

def log_info(msg: str):
    print(f"[INFO] {msg}")

def log_warn(msg: str):
    print(f"[WARN] {msg}", file=sys.stderr)

def log_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)


# =============================================================================
#  LECTURA DE FUENTES DE ENTRADA
# =============================================================================

def read_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Lee un archivo JSONL y retorna lista de objetos."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                log_warn(f"Line {line_num} en {filepath}: JSON invalido ({e})")
    log_info(f"Leidos {len(records)} registros de JSONL: {filepath}")
    return records


def read_json(filepath: str) -> List[Dict[str, Any]]:
    """Lee un archivo JSON (array o objeto) y retorna lista de papers."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        log_info(f"Leidos {len(data)} registros de JSON array: {filepath}")
        return data
    elif isinstance(data, dict):
        # Podria ser un unico paper o un objeto con clave "papers"
        if "papers" in data and isinstance(data["papers"], list):
            log_info(f"Leidos {len(data['papers'])} registros de JSON (clave 'papers'): {filepath}")
            return data["papers"]
        else:
            log_info(f"Leido 1 registro de JSON objeto: {filepath}")
            return [data]
    else:
        log_warn(f"Formato JSON no reconocido en {filepath}")
        return []


def read_gunjs_folder(folder_path: str) -> List[Dict[str, Any]]:
    """Lee una carpeta con archivos JSON de Gun.js (radata/)."""
    records = []
    pattern = os.path.join(folder_path, "**/*.json")
    files = glob.glob(pattern, recursive=True)
    log_info(f"Encontrados {len(files)} archivos JSON en {folder_path}")

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                records.extend(data)
            elif isinstance(data, dict):
                records.append(data)
        except Exception as e:
            log_warn(f"Error leyendo {filepath}: {e}")

    log_info(f"Leidos {len(records)} registros totales de carpeta Gun.js")
    return records


def read_zip(filepath: str) -> List[Dict[str, Any]]:
    """Extrae y lee papers desde un ZIP de backup."""
    records = []
    temp_dir = os.path.join(os.path.dirname(filepath), ".tmp_extract")
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(filepath, "r") as z:
        json_files = [n for n in z.namelist() if n.lower().endswith((".json", ".jsonl"))]
        log_info(f"Encontrados {len(json_files)} archivos JSON/JSONL en ZIP")

        for fname in json_files:
            try:
                z.extract(fname, temp_dir)
                extracted_path = os.path.join(temp_dir, fname)
                if fname.lower().endswith(".jsonl"):
                    records.extend(read_jsonl(extracted_path))
                else:
                    records.extend(read_json(extracted_path))
            except Exception as e:
                log_warn(f"Error extrayendo {fname}: {e}")

    log_info(f"Leidos {len(records)} registros totales de ZIP")
    return records


def detect_and_read_input(input_path: str) -> List[Dict[str, Any]]:
    """Auto-detecta el tipo de entrada y lee los papers."""
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encuentra la ruta de entrada: {input_path}")

    if path.is_dir():
        return read_gunjs_folder(str(path))

    ext = path.suffix.lower()
    if ext == ".jsonl":
        return read_jsonl(str(path))
    elif ext == ".json":
        return read_json(str(path))
    elif ext == ".zip":
        return read_zip(str(path))
    else:
        raise ValueError(f"Formato de entrada no soportado: {ext}")


# =============================================================================
#  PROCESAMIENTO Y VALIDACION DE PAPERS
# =============================================================================

def normalize_paper(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normaliza un paper crudo al esquema estandar de P2PCLAW.
    Retorna None si el paper es invalido/incompleto.
    """
    paper: Dict[str, Any] = {}

    # Campos obligatorios
    title = raw.get("title", raw.get("name", raw.get("paper_title", "")))
    content = raw.get("content", raw.get("body", raw.get("text", raw.get("markdown", ""))))

    if not title or not content:
        return None  # Paper sin titulo o contenido = descartar

    paper["title"] = str(title).strip()
    paper["content"] = str(content).strip()

    # Metadatos opcionales con defaults seguros
    paper["granular_scores"] = raw.get("granular_scores", raw.get("scores", {}))
    paper["lean_verified"] = bool(raw.get("lean_verified", raw.get("verified", False)))
    paper["agent_id"] = str(raw.get("agent_id", raw.get("agent", "unknown")))
    paper["model"] = str(raw.get("model", raw.get("agent_model", "unknown")))
    paper["tier"] = str(raw.get("tier", "UNKNOWN")).upper()
    paper["word_count"] = int(raw.get("word_count", raw.get("words", 0)))
    paper["timestamp"] = raw.get("timestamp", raw.get("created_at", ""))
    paper["id"] = str(raw.get("id", raw.get("_id", raw.get("paper_id", ""))))

    # Campos adicionales que pueden ser utiles
    paper["tags"] = raw.get("tags", raw.get("keywords", []))
    paper["domain"] = str(raw.get("domain", raw.get("field", "general")))

    # Normalizar granular_scores si no existe
    if not isinstance(paper["granular_scores"], dict):
        paper["granular_scores"] = {}

    return paper


def compute_overall_score(paper: Dict[str, Any]) -> float:
    """
    Calcula un score promedio del paper basado en granular_scores.
    Si no hay scores, retorna 5.0 como default neutral.
    """
    scores = paper.get("granular_scores", {})
    if not scores:
        return 5.0

    # Priorizar scores de secciones principales
    section_keys = ["abstract", "introduction", "methodology",
                    "results", "discussion", "conclusion", "references"]
    quality_keys = ["novelty", "reproducibility", "citations"]

    values = []
    for key in section_keys + quality_keys:
        val = scores.get(key)
        if isinstance(val, (int, float)) and 0 <= val <= 10:
            values.append(float(val))

    if not values:
        return 5.0

    return sum(values) / len(values)


def extract_sections(content: str) -> Dict[str, str]:
    """
    Extrae secciones del contenido markdown usando headers ##.
    Retorna dict con {section_name: section_content}.
    """
    sections: Dict[str, str] = {}
    # Headers markdown: ## Abstract, ## Introduction, etc.
    pattern = re.compile(r'##\s*(.+?)\n(.*?)(?=\n##\s|\Z)', re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(content)

    for header, body in matches:
        key = header.strip().lower().replace(" ", "_")
        sections[key] = body.strip()

    # Fallback: si no hay headers, tratar todo como contenido plano
    if not sections and content.strip():
        sections["full_text"] = content.strip()

    return sections


def estimate_tokens(text: str) -> int:
    """
    Estima numero de tokens usando aproximacion 0.75 tokens/palabra (GPT-style).
    """
    words = len(text.split())
    return int(words / 0.75)


# =============================================================================
#  GENERACION DE FORMATOS DE CONVERSACION
# =============================================================================

def build_conversation(
    system: str,
    user: str,
    assistant: str,
    thinking: Optional[str] = None,
    tool_call: Optional[str] = None,
    tool_result: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Construye un objeto de conversacion en formato messages estandar.
    """
    messages: List[Dict[str, str]] = [{"role": "system", "content": system}]

    if tool_call and tool_result:
        # Modo tool use: user → assistant(tool_call) → tool_result → assistant(final)
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": tool_call})
        messages.append({"role": "tool", "content": tool_result})
        messages.append({"role": "assistant", "content": assistant})
    elif thinking:
        # Modo thinking: el assistant incluye razonamiento antes de la respuesta
        content = f"<thinking>\n{thinking}\n</thinking>\n\n{assistant}"
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": content})
    else:
        # Modo estandar
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})

    return {"messages": messages}


def build_assistant_content(paper: Dict[str, Any]) -> str:
    """
    Construye el contenido del assistant evitando duplicar el titulo
    si ya esta presente al inicio del contenido markdown.
    """
    title = paper["title"]
    content = paper["content"]
    # Verificar si el contenido ya comienza con el titulo como header
    content_start = content.lstrip()[:120]  # primeros 120 chars
    if re.search(rf'^#\s+{re.escape(title)}', content_start, re.IGNORECASE):
        return content
    return f"# {title}\n\n{content}"


def format_qwen3(paper: Dict[str, Any], prompt_variant: int = 0,
                  thinking: Optional[str] = None,
                  tool_call: Optional[str] = None,
                  tool_result: Optional[str] = None) -> Dict[str, Any]:
    """
    Formatea un paper al formato Qwen3 de conversacion.
    """
    system = FORMAT_TEMPLATES["qwen3"]["system"]
    user_prompt = PAPER_GENERATION_PROMPTS[prompt_variant % len(PAPER_GENERATION_PROMPTS)]
    user = user_prompt.format(title=paper["title"])
    assistant = build_assistant_content(paper)

    return build_conversation(system, user, assistant, thinking, tool_call, tool_result)


def format_gemma(paper: Dict[str, Any], prompt_variant: int = 0,
                 thinking: Optional[str] = None,
                 tool_call: Optional[str] = None,
                 tool_result: Optional[str] = None) -> Dict[str, Any]:
    """
    Formatea un paper al formato Gemma 4 de conversacion.
    Gemma usa el mismo JSON de messages; la diferencia esta en el chat template
    aplicado durante el entrenamiento. Generamos el mismo JSON base.
    """
    system = FORMAT_TEMPLATES["gemma"]["system"]
    user_prompt = PAPER_GENERATION_PROMPTS[prompt_variant % len(PAPER_GENERATION_PROMPTS)]
    user = user_prompt.format(title=paper["title"])
    assistant = build_assistant_content(paper)

    return build_conversation(system, user, assistant, thinking, tool_call, tool_result)


def format_generic(paper: Dict[str, Any], prompt_variant: int = 0,
                   thinking: Optional[str] = None,
                   tool_call: Optional[str] = None,
                   tool_result: Optional[str] = None) -> Dict[str, Any]:
    """Formato generico compatible con multiples modelos."""
    system = FORMAT_TEMPLATES["generic"]["system"]
    user_prompt = PAPER_GENERATION_PROMPTS[prompt_variant % len(PAPER_GENERATION_PROMPTS)]
    user = user_prompt.format(title=paper["title"])
    assistant = build_assistant_content(paper)

    return build_conversation(system, user, assistant, thinking, tool_call, tool_result)


def format_paper(paper: Dict[str, Any], fmt: str = "qwen3",
                   prompt_variant: int = 0,
                   thinking: Optional[str] = None,
                   tool_call: Optional[str] = None,
                   tool_result: Optional[str] = None) -> Dict[str, Any]:
    """Dispatcher de formato."""
    if fmt == "qwen3":
        return format_qwen3(paper, prompt_variant, thinking, tool_call, tool_result)
    elif fmt == "gemma":
        return format_gemma(paper, prompt_variant, thinking, tool_call, tool_result)
    else:
        return format_generic(paper, prompt_variant, thinking, tool_call, tool_result)


# =============================================================================
#  GENERACION DE DATASETS ESPECIALIZADOS
# =============================================================================

def generate_reasoning_examples(papers: List[Dict[str, Any]], fmt: str,
                                max_per_paper: int = 3) -> List[Dict[str, Any]]:
    """
    Genera ejemplos de reasoning/thinking a partir de papers.
    Cada paper puede generar hasta max_per_paper ejemplos con distintos prompts.
    """
    examples = []
    for paper in papers:
        sections = extract_sections(paper["content"])
        scores = paper.get("granular_scores", {})

        # Seleccionar prompts aleatorios de reasoning
        num_examples = min(max_per_paper, len(REASONING_PROMPTS))
        selected_prompts = REASONING_PROMPTS[:num_examples]

        for i, rp in enumerate(selected_prompts):
            user = rp.format(title=paper["title"])

            # Construir thinking context-aware
            method_desc = "a mixed-methods approach" if "methodology" in sections else "the described experimental protocol"
            sample_assessment = "adequate" if scores.get("methodology", 5) >= 7 else "potentially underpowered"
            confounders = "selection bias, measurement error" if scores.get("reproducibility", 5) < 7 else "minimal identified confounders"
            repro = scores.get("reproducibility", 5)
            overall = "sound and well-documented" if repro >= 7 else "in need of additional validation"

            thinking_text = (
                f"Let me analyze this step by step.\n"
                f"1. The paper '{paper['title']}' addresses a research question in {paper.get('domain', 'its field')}.\n"
                f"2. Looking at the methodology: it uses {method_desc}.\n"
                f"3. The sample size appears {sample_assessment} for the stated objectives.\n"
                f"4. Potential issues: {confounders}.\n"
                f"5. Reproducibility score: {repro}/10.\n"
                f"6. Overall: the methodology is {overall}.\n"
                f"7. Key strengths: {', '.join([k for k,v in scores.items() if isinstance(v, (int,float)) and v >= 8]) or 'notable effort in structure'}.\n"
                f"8. Areas for improvement: {', '.join([k for k,v in scores.items() if isinstance(v, (int,float)) and v < 6]) or 'none major identified'}."
            )

            # Respuesta final del assistant (resumen analitico)
            final = (
                f"Analysis of '{paper['title']}':\n\n"
                f"**Methodology**: The paper employs {method_desc}. "
                f"With a reproducibility score of {repro}/10, the approach is {overall}.\n\n"
                f"**Statistical Rigor**: The analysis shows {sample_assessment} power. "
                f"Confounders ({confounders}) are {('well-addressed' if repro >= 7 else 'insufficiently controlled')}.\n\n"
                f"**Novelty Score**: {scores.get('novelty', 'N/A')}/10. "
                f"The contribution is {('significant' if scores.get('novelty', 5) >= 7 else 'incremental')}.\n\n"
                f"**Citations**: {scores.get('citations', 'N/A')}/10. "
                f"References are {('comprehensive and current' if scores.get('citations', 5) >= 7 else 'could be expanded')}.\n\n"
                f"**Verdict**: {'RECOMMENDED' if compute_overall_score(paper) >= 7 else 'ACCEPTABLE WITH REVISIONS' if compute_overall_score(paper) >= 5 else 'NEEDS SUBSTANTIAL REVISION'}."
            )

            conv = build_conversation(
                system=FORMAT_TEMPLATES[fmt]["system"],
                user=user,
                assistant=final,
                thinking=thinking_text,
            )
            examples.append(conv)

    return examples


def generate_tooluse_examples(papers: List[Dict[str, Any]], fmt: str,
                              max_per_paper: int = 2) -> List[Dict[str, Any]]:
    """
    Genera ejemplos de tool use (Python, Lean 4, Search) a partir de papers.
    """
    examples = []
    tool_types = list(TOOL_USE_TEMPLATES.keys())

    for paper in papers:
        scores = paper.get("granular_scores", {})
        sections = extract_sections(paper["content"])

        # Seleccionar herramientas relevantes para este paper
        selected_tools = []
        if scores.get("methodology", 5) >= 6 or "results" in sections:
            selected_tools.append("python")
        if scores.get("novelty", 5) >= 6 or "abstract" in sections:
            selected_tools.append("lean4")
        if scores.get("citations", 5) >= 5:
            selected_tools.append("search")

        if not selected_tools:
            selected_tools = ["python"]

        num_examples = min(max_per_paper, len(selected_tools))
        for i in range(num_examples):
            tool = selected_tools[i % len(selected_tools)]
            tmpl = TOOL_USE_TEMPLATES[tool]

            user_prompt = tmpl["user_prompts"][i % len(tmpl["user_prompts"])]
            user = user_prompt.format(title=paper["title"])

            tool_call = tmpl["tool_call"].format(
                title=paper["title"],
                method=paper.get("domain", "mixed-methods"),
                n=paper.get("word_count", 1000) // 50,  # aprox sample size
            )
            tool_result = tmpl["tool_result"]
            final = tmpl["final_answer"].format(title=paper["title"])

            conv = build_conversation(
                system=FORMAT_TEMPLATES[fmt]["system"],
                user=user,
                assistant=final,
                tool_call=tool_call,
                tool_result=tool_result,
            )
            examples.append(conv)

    return examples


# =============================================================================
#  ESCRITURA DE DATASETS
# =============================================================================

def write_jsonl(records: List[Dict[str, Any]], filepath: str):
    """Escribe una lista de records a un archivo JSONL."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    log_info(f"Escritos {len(records)} registros a {filepath}")


def build_dataset_name(base: str, suffix: str, fmt: str) -> str:
    """Construye nombre de archivo dataset."""
    return f"{base}_{suffix}_{fmt}.jsonl"


# =============================================================================
#  ESTADISTICAS
# =============================================================================

def compute_statistics(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula estadisticas agregadas del dataset."""
    if not papers:
        return {}

    total = len(papers)
    scores = [compute_overall_score(p) for p in papers]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Distribucion por tier
    tier_counts = Counter(p.get("tier", "UNKNOWN") for p in papers)

    # Distribucion por modelo
    model_counts = Counter(p.get("model", "unknown") for p in papers)

    # Distribucion por lean_verified
    verified_count = sum(1 for p in papers if p.get("lean_verified", False))

    # Tokens estimados
    total_tokens = sum(estimate_tokens(p.get("content", "")) for p in papers)
    avg_tokens = total_tokens // total if total else 0

    # Distribucion por score (buckets)
    score_buckets = {
        "0-4.9": sum(1 for s in scores if s < 5),
        "5.0-6.9": sum(1 for s in scores if 5 <= s < 7),
        "7.0-8.9": sum(1 for s in scores if 7 <= s < 9),
        "9.0-10": sum(1 for s in scores if s >= 9),
    }

    # Word counts
    word_counts = [p.get("word_count", 0) for p in papers]
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0

    return {
        "total_papers": total,
        "avg_score": round(avg_score, 2),
        "avg_words": round(avg_words, 1),
        "total_tokens_estimated": total_tokens,
        "avg_tokens_per_paper": avg_tokens,
        "verified_count": verified_count,
        "verified_pct": round(100 * verified_count / total, 1) if total else 0,
        "tier_distribution": dict(tier_counts),
        "model_distribution": dict(model_counts),
        "score_distribution": score_buckets,
        "timestamp": datetime.now().isoformat(),
    }


def print_statistics(stats: Dict[str, Any]):
    """Imprime estadisticas formateadas en consola."""
    if not stats:
        log_warn("No hay estadisticas para mostrar.")
        return

    print("\n" + "=" * 70)
    print("  ESTADISTICAS DEL DATASET P2PCLAW")
    print("=" * 70)
    print(f"  Total de papers procesados      : {stats['total_papers']}")
    print(f"  Score promedio                  : {stats['avg_score']}/10")
    print(f"  Promedio de palabras/paper       : {stats['avg_words']}")
    print(f"  Tokens estimados (total)        : {stats['total_tokens_estimated']:,}")
    print(f"  Tokens estimados (promedio)      : {stats['avg_tokens_per_paper']:,}")
    print(f"  Papers verificados (Lean)        : {stats['verified_count']} ({stats['verified_pct']}%)")
    print("-" * 70)
    print("  Distribucion por TIER:")
    for tier, count in sorted(stats["tier_distribution"].items()):
        print(f"    {tier:12s} : {count:4d} papers")
    print("-" * 70)
    print("  Distribucion por MODELO:")
    for model, count in sorted(stats["model_distribution"].items(), key=lambda x: -x[1]):
        print(f"    {model:30s} : {count:4d} papers")
    print("-" * 70)
    print("  Distribucion por SCORE:")
    for bucket, count in stats["score_distribution"].items():
        print(f"    {bucket:12s} : {count:4d} papers")
    print("=" * 70)
    print(f"  Generado el: {stats['timestamp']}")
    print("=" * 70 + "\n")


def write_statistics(stats: Dict[str, Any], output_dir: str):
    """Escribe estadisticas a un archivo JSON."""
    stats_path = os.path.join(output_dir, "dataset_statistics.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    log_info(f"Estadisticas guardadas en {stats_path}")


# =============================================================================
#  PIPELINE PRINCIPAL
# =============================================================================

def run_pipeline(args):
    """
    Ejecuta el pipeline completo de conversion.
    """
    # ------------------------------------------------------------------
    # 1. Leer entrada
    # ------------------------------------------------------------------
    log_info(f"Leyendo entrada desde: {args.input}")
    raw_records = detect_and_read_input(args.input)
    log_info(f"Registros crudos leidos: {len(raw_records)}")

    # ------------------------------------------------------------------
    # 2. Normalizar y validar papers
    # ------------------------------------------------------------------
    papers: List[Dict[str, Any]] = []
    rejected = 0
    for raw in raw_records:
        paper = normalize_paper(raw)
        if paper:
            papers.append(paper)
        else:
            rejected += 1

    log_info(f"Papers validos: {len(papers)} | Rechazados: {rejected}")

    if not papers:
        log_error("No se encontraron papers validos. Abortando.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 3. Calcular scores
    # ------------------------------------------------------------------
    for p in papers:
        p["_overall_score"] = compute_overall_score(p)

    # ------------------------------------------------------------------
    # 4. Aplicar filtros
    # ------------------------------------------------------------------
    min_score = args.min_score
    log_info(f"Filtrando papers con score >= {min_score}")

    papers_full = papers
    papers_verified = [p for p in papers if p.get("lean_verified", False)]
    papers_hq = [p for p in papers if p["_overall_score"] >= min_score]

    log_info(f"  Full dataset    : {len(papers_full)}")
    log_info(f"  Verified dataset: {len(papers_verified)}")
    log_info(f"  HQ dataset      : {len(papers_hq)} (score >= {min_score})")

    # ------------------------------------------------------------------
    # 5. Generar datasets de conversacion
    # ------------------------------------------------------------------
    fmt = args.format.lower()
    if fmt not in FORMAT_TEMPLATES:
        log_warn(f"Formato '{fmt}' no reconocido, usando 'generic'")
        fmt = "generic"

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    base_name = args.output_prefix

    # Dataset FULL
    records_full = [format_paper(p, fmt, i % len(PAPER_GENERATION_PROMPTS))
                    for i, p in enumerate(papers_full)]
    write_jsonl(records_full,
                os.path.join(output_dir, build_dataset_name(base_name, "full", fmt)))

    # Dataset VERIFIED
    if papers_verified:
        records_verified = [format_paper(p, fmt, i % len(PAPER_GENERATION_PROMPTS))
                            for i, p in enumerate(papers_verified)]
        write_jsonl(records_verified,
                    os.path.join(output_dir, build_dataset_name(base_name, "verified", fmt)))
    else:
        log_warn("No hay papers verificados; dataset omitido.")

    # Dataset HQ
    if papers_hq:
        records_hq = [format_paper(p, fmt, i % len(PAPER_GENERATION_PROMPTS))
                      for i, p in enumerate(papers_hq)]
        write_jsonl(records_hq,
                    os.path.join(output_dir, build_dataset_name(base_name, "hq", fmt)))
    else:
        log_warn("No hay papers HQ; dataset omitido.")

    # Dataset REASONING (opcional)
    if args.include_reasoning:
        log_info("Generando dataset de reasoning/thinking...")
        reasoning_source = papers_hq if papers_hq else papers_full
        reasoning_limit = min(args.reasoning_max, len(reasoning_source))
        records_reasoning = generate_reasoning_examples(
            reasoning_source[:reasoning_limit], fmt,
            max_per_paper=args.reasoning_per_paper
        )
        write_jsonl(records_reasoning,
                    os.path.join(output_dir, build_dataset_name(base_name, "reasoning", fmt)))

    # Dataset TOOL USE (opcional)
    if args.include_tooluse:
        log_info("Generando dataset de tool use...")
        tooluse_source = papers_hq if papers_hq else papers_full
        tooluse_limit = min(args.tooluse_max, len(tooluse_source))
        records_tooluse = generate_tooluse_examples(
            tooluse_source[:tooluse_limit], fmt,
            max_per_paper=args.tooluse_per_paper
        )
        write_jsonl(records_tooluse,
                    os.path.join(output_dir, build_dataset_name(base_name, "tooluse", fmt)))

    # ------------------------------------------------------------------
    # 6. Estadisticas
    # ------------------------------------------------------------------
    log_info("Calculando estadisticas...")
    stats = compute_statistics(papers)
    print_statistics(stats)
    write_statistics(stats, output_dir)

    # ------------------------------------------------------------------
    # 7. Metadata del pipeline
    # ------------------------------------------------------------------
    metadata = {
        "pipeline": "cajal_to_training",
        "version": "1.0.0",
        "input_path": args.input,
        "output_dir": output_dir,
        "format": fmt,
        "min_score": min_score,
        "include_reasoning": args.include_reasoning,
        "include_tooluse": args.include_tooluse,
        "papers_total": len(papers),
        "papers_verified": len(papers_verified),
        "papers_hq": len(papers_hq),
        "statistics": stats,
        "generated_at": datetime.now().isoformat(),
    }
    meta_path = os.path.join(output_dir, "pipeline_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    log_info(f"Metadata guardada en {meta_path}")

    log_info("Pipeline completado exitosamente!")
    return metadata


# =============================================================================
#  CLI - ARGUMENT PARSER
# =============================================================================

def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="convert_cajal_to_training.py",
        description=(
            "Convierte papers de P2PCLAW al formato de conversacion "
            "(chat/JSONL) para fine-tuning de LLMs."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Basico: convertir a formato Qwen3
  python convert_cajal_to_training.py --input papers.jsonl --output-dir ./datasets

  # Con filtros de calidad y reasoning
  python convert_cajal_to_training.py \\
      --input papers.jsonl \\
      --output-dir ./datasets \\
      --min-score 7.0 \\
      --format qwen3 \\
      --include-reasoning \\
      --include-tooluse

  # Desde carpeta Gun.js (radata/)
  python convert_cajal_to_training.py --input ./radata --output-dir ./datasets

  # Desde ZIP de backup
  python convert_cajal_to_training.py --input backup.zip --output-dir ./datasets

  # Solo dataset full, sin extras
  python convert_cajal_to_training.py \\
      --input papers.jsonl \\
      --output-dir ./datasets \\
      --no-reasoning \\
      --no-tooluse
        """,
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Ruta de entrada: archivo .jsonl, .json, carpeta, o .zip",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="./datasets",
        help="Directorio de salida para los datasets (default: ./datasets)",
    )
    parser.add_argument(
        "--output-prefix",
        default="p2pclaw_train",
        help="Prefijo para los nombres de archivo de salida (default: p2pclaw_train)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["qwen3", "gemma", "generic"],
        default="qwen3",
        help="Formato de salida: qwen3 | gemma | generic (default: qwen3)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=7.0,
        help="Score minimo para dataset HQ (default: 7.0)",
    )
    parser.add_argument(
        "--include-reasoning",
        action="store_true",
        default=True,
        help="Incluir dataset de reasoning/thinking (default: True)",
    )
    parser.add_argument(
        "--no-reasoning",
        action="store_false",
        dest="include_reasoning",
        help="Omitir dataset de reasoning/thinking",
    )
    parser.add_argument(
        "--reasoning-max",
        type=int,
        default=500,
        help="Maximo de papers a usar para dataset reasoning (default: 500)",
    )
    parser.add_argument(
        "--reasoning-per-paper",
        type=int,
        default=3,
        help="Ejemplos de reasoning por paper (default: 3)",
    )
    parser.add_argument(
        "--include-tooluse",
        action="store_true",
        default=True,
        help="Incluir dataset de tool use (default: True)",
    )
    parser.add_argument(
        "--no-tooluse",
        action="store_false",
        dest="include_tooluse",
        help="Omitir dataset de tool use",
    )
    parser.add_argument(
        "--tooluse-max",
        type=int,
        default=500,
        help="Maximo de papers a usar para dataset tooluse (default: 500)",
    )
    parser.add_argument(
        "--tooluse-per-paper",
        type=int,
        default=2,
        help="Ejemplos de tool use por paper (default: 2)",
    )

    return parser


# =============================================================================
#  PUNTO DE ENTRADA
# =============================================================================

def main():
    parser = build_argument_parser()
    args = parser.parse_args()

    log_info("=" * 60)
    log_info("P2PCLAW Dataset Converter v1.0")
    log_info("=" * 60)
    log_info(f"Input : {args.input}")
    log_info(f"Output: {args.output_dir}")
    log_info(f"Format: {args.format}")
    log_info(f"MinScore: {args.min_score}")
    log_info(f"Reasoning: {args.include_reasoning}")
    log_info(f"ToolUse: {args.include_tooluse}")
    log_info("=" * 60)

    try:
        run_pipeline(args)
    except FileNotFoundError as e:
        log_error(str(e))
        sys.exit(2)
    except Exception as e:
        log_error(f"Error inesperado: {e}")
        raise


if __name__ == "__main__":
    main()
