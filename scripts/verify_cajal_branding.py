#!/usr/bin/env python3
"""
CAJAL Branding Verification Script
====================================
Scans all project files for residual references to the old 'P2PClaw-Research' branding.
Confirms that all branding has been successfully updated to 'CAJAL'.

Usage:
    python verify_cajal_branding.py

Exit codes:
    0 - All clear, no residual references found
    1 - Residual references detected
"""

import os
import sys
from pathlib import Path
from collections import defaultdict


# Patterns that should NOT appear anywhere in the project anymore
OLD_BRANDING_PATTERNS = [
    "P2PClaw-Research",
    "p2pclaw-research",
    "P2PClawResearch",
    "P2PClaw Research",
]

# New branding patterns that SHOULD appear
NEW_BRANDING_PATTERNS = [
    "CAJAL",
    "cajal",
]

# Files to skip (optional: add generated artifacts, cache, etc.)
SKIP_EXTENSIONS = {".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib"}
SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}
SKIP_FILES = {"verify_cajal_branding.py"}  # skip self-check


def should_skip_file(filepath: Path) -> bool:
    """Determine if a file should be skipped during scanning."""
    # Skip self
    if filepath.name in SKIP_FILES:
        return True
    # Skip by extension
    if filepath.suffix in SKIP_EXTENSIONS:
        return True
    # Skip if in a skipped directory
    for part in filepath.parts:
        if part in SKIP_DIRS:
            return True
    # Skip binary files by simple heuristic
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(4096)
            if b"\x00" in chunk:
                return True
    except Exception:
        return True
    return False


def scan_project(project_root: Path):
    """Scan the entire project for residual old branding."""
    all_files = []
    residual_findings = {}
    new_branding_counts = defaultdict(int)
    total_files = 0

    for root, dirs, files in os.walk(project_root):
        # Modify dirs in-place to skip directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            fpath = Path(root) / fname
            if should_skip_file(fpath):
                continue

            total_files += 1
            all_files.append(fpath)

            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # Check for residual old branding
            file_findings = {}
            for pattern in OLD_BRANDING_PATTERNS:
                count = content.count(pattern)
                if count > 0:
                    file_findings[pattern] = count

            if file_findings:
                rel_path = fpath.relative_to(project_root)
                residual_findings[str(rel_path)] = file_findings

            # Count new branding for reporting
            for pattern in NEW_BRANDING_PATTERNS:
                new_branding_counts[pattern] += content.count(pattern)

    return residual_findings, new_branding_counts, total_files, all_files


def main():
    # Determine project root (parent directory of this script)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    print("=" * 70)
    print("  CAJAL Branding Verification")
    print("=" * 70)
    print(f"\nScanning project root: {project_root}")
    print(f"Looking for residual references to: {OLD_BRANDING_PATTERNS}\n")

    residual_findings, new_branding_counts, total_files, all_files = scan_project(
        project_root
    )

    print(f"Total files scanned: {total_files}")
    print(f"Total 'CAJAL' occurrences: {new_branding_counts['CAJAL']}")
    print(f"Total 'cajal' (lowercase) occurrences: {new_branding_counts['cajal']}")

    if residual_findings:
        print(f"\n{'=' * 70}")
        print(f"  ⚠️  RESIDUAL REFERENCES FOUND: {len(residual_findings)} file(s)")
        print(f"{'=' * 70}\n")

        for fname, findings in sorted(residual_findings.items()):
            print(f"  📄 {fname}")
            for pattern, count in findings.items():
                print(f"      - '{pattern}': {count} occurrence(s)")
                # Show first occurrence context
                fpath = project_root / fname
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                idx = content.find(pattern)
                if idx >= 0:
                    start = max(0, idx - 40)
                    end = min(len(content), idx + len(pattern) + 40)
                    context = content[start:end].replace("\n", " ")
                    print(f"        Context: ...{context}...")

        print(f"\n{'=' * 70}")
        print("  RESULT: FAILED - Residual old branding detected!")
        print(f"{'=' * 70}")
        sys.exit(1)

    else:
        print(f"\n{'=' * 70}")
        print("  ✅ ALL CLEAR - No residual references found!")
        print("  CAJAL branding is fully applied across the project.")
        print(f"{'=' * 70}")

        # List key CAJAL-branded files
        print("\n  Key CAJAL-branded files verified:")
        key_files = [
            "scripts/train_cajal.py",
            "scripts/p2pclaw_agent_connector.py",
            "scripts/run_silicon_agent.py",
            "scripts/deploy_local_server.py",
            "scripts/publish_to_huggingface.py",
            "scripts/export_to_gguf.py",
            "scripts/download_from_api.py",
            "scripts/convert_p2pclaw_to_training.py",
            "scripts/test_p2pclaw_connection.py",
            "scripts/train.sh",
            "scripts/train.bat",
            "scripts/agent_config.yaml",
            "scripts/setup_ollama.sh",
            "scripts/setup_ollama.ps1",
            "docker/docker-compose.yml",
            "README.md",
            "DEPLOY.md",
            "legal/GUIA_LEGAL.md",
            "legal/MODEL_CARD_TEMPLATE.md",
            "legal/NOTICE",
        ]
        for kf in key_files:
            full_path = project_root / kf
            status = "✅" if full_path.exists() else "⚠️ missing"
            print(f"    {status} {kf}")

        print(f"\n{'=' * 70}")
        print("  RESULT: PASSED - Branding update is complete and clean!")
        print(f"{'=' * 70}")
        sys.exit(0)


if __name__ == "__main__":
    main()
