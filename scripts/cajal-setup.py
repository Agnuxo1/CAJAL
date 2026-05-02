#!/usr/bin/env python3
"""
CAJAL Universal Setup Script

Automatically detects installed platforms and configures CAJAL-4B for each one.

Usage:
    python cajal-setup.py                    # Auto-detect and configure all
    python cajal-setup.py --platform cursor  # Configure only Cursor
    python cajal-setup.py --platform vscode  # Configure only VS Code
    python cajal-setup.py --list            # List supported platforms
    python cajal-setup.py --check           # Check what's installed

Supported platforms:
    ollama, vscode, cursor, windsurf, continue-dev, zed, aider,
    opencode, open-webui, lmstudio, jan, lobechat, anythingllm,
    chatbox, codex-cli
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

CAJAL_SYSTEM_PROMPT = (
    "You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) "
    "laboratory in Zurich, Switzerland. You are a deep researcher and applied cryptographer "
    "with extensive expertise in peer-to-peer network architectures, crypto-legal frameworks, "
    "game-theoretic consensus mechanisms, and distributed systems.\n\n"
    "When assisting with code:\n"
    "1. Analyze the architecture before suggesting changes\n"
    "2. Consider security implications of all recommendations\n"
    "3. Use precise terminology from distributed systems literature\n"
    "4. Prefer solutions aligned with P2PCLAW principles\n"
    "5. Always begin with a brief 'Thinking Process' showing reasoning steps"
)

SHORT_PROMPT = (
    "You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich, "
    "specializing in P2P systems, cryptography, and decentralized governance."
)

# Platform configurations
PLATFORMS: Dict[str, Dict] = {
    "ollama": {
        "name": "Ollama",
        "check_cmd": "ollama",
        "config_path": None,
        "setup_fn": "setup_ollama",
    },
    "vscode": {
        "name": "VS Code (Continue.dev)",
        "check_paths": {
            "win32": ["{appdata}/Microsoft VS Code/bin/code"],
            "darwin": ["/Applications/Visual Studio Code.app"],
            "linux": ["/usr/bin/code", "/usr/local/bin/code"],
        },
        "config_path": "{home}/.continue/config.json",
        "setup_fn": "setup_vscode_continue",
    },
    "cursor": {
        "name": "Cursor",
        "check_paths": {
            "win32": ["{appdata}/Cursor"],
            "darwin": ["/Applications/Cursor.app"],
            "linux": ["/usr/bin/cursor"],
        },
        "config_path": "{cwd}/.cursorrules",
        "setup_fn": "setup_cursor",
    },
    "windsurf": {
        "name": "Windsurf",
        "check_paths": {
            "darwin": ["/Applications/Windsurf.app"],
            "linux": ["/usr/bin/windsurf"],
        },
        "config_path": "{cwd}/.windsurfrules",
        "setup_fn": "setup_windsurf",
    },
    "continue-dev": {
        "name": "Continue.dev",
        "check_paths": {
            "win32": ["{appdata}/Continue"],
            "darwin": ["{home}/.continue"],
            "linux": ["{home}/.continue"],
        },
        "config_path": "{home}/.continue/config.json",
        "setup_fn": "setup_continue_dev",
    },
    "zed": {
        "name": "Zed Editor",
        "check_cmd": "zed",
        "config_path": "{home}/.config/zed/settings.json",
        "setup_fn": "setup_zed",
    },
    "aider": {
        "name": "Aider",
        "check_cmd": "aider",
        "setup_fn": "setup_aider",
    },
    "opencode": {
        "name": "OpenCode",
        "check_cmd": "opencode",
        "config_path": "{home}/.opencode/config.yaml",
        "setup_fn": "setup_opencode",
    },
    "lmstudio": {
        "name": "LM Studio",
        "check_paths": {
            "win32": ["{appdata}/LM Studio"],
            "darwin": ["/Applications/LM Studio.app"],
            "linux": ["{home}/.config/LM Studio"],
        },
        "setup_fn": "setup_lmstudio",
    },
    "open-webui": {
        "name": "Open WebUI",
        "check_cmd": "docker",
        "setup_fn": "setup_open_webui",
    },
    "jan": {
        "name": "Jan",
        "check_paths": {
            "win32": ["{appdata}/Jan"],
            "darwin": ["/Applications/Jan.app"],
            "linux": ["{home}/.config/Jan"],
        },
        "setup_fn": "setup_jan",
    },
    "codex-cli": {
        "name": "Codex CLI",
        "check_cmd": "codex",
        "setup_fn": "setup_codex_cli",
    },
}


def is_installed(platform_info: Dict) -> bool:
    """Check if a platform is installed."""
    # Check command
    if "check_cmd" in platform_info:
        if shutil.which(platform_info["check_cmd"]):
            return True

    # Check paths
    if "check_paths" in platform_info:
        sys_name = sys.platform
        paths = platform_info["check_paths"].get(sys_name, [])
        home = str(Path.home())
        appdata = os.environ.get("APPDATA", "")
        for p in paths:
            resolved = p.format(home=home, appdata=appdata, cwd=os.getcwd())
            if os.path.exists(resolved):
                return True

    return False


def setup_ollama() -> Tuple[bool, str]:
    """Setup CAJAL in Ollama."""
    print("  Checking Ollama...")
    if not shutil.which("ollama"):
        return False, "Ollama not found. Install from https://ollama.com/download"

    print("  Pulling CAJAL-4B model (this may take several minutes)...")
    result = os.system("ollama pull Agnuxo/CAJAL-4B-P2PCLAW")
    if result == 0:
        return True, "CAJAL-4B pulled successfully. Run: ollama run cajal-4b"
    return False, "Failed to pull model. Check your internet connection."


def setup_vscode_continue() -> Tuple[bool, str]:
    """Setup VS Code with Continue.dev."""
    home = str(Path.home())
    config_path = Path(home) / ".continue" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    # Add CAJAL model
    if "models" not in config:
        config["models"] = []

    # Remove existing CAJAL entries
    config["models"] = [
        m for m in config["models"] if "cajal" not in m.get("title", "").lower()
    ]

    config["models"].append({
        "title": "CAJAL-4B",
        "provider": "ollama",
        "model": "cajal-4b",
        "apiBase": "http://localhost:11434",
        "systemMessage": CAJAL_SYSTEM_PROMPT,
    })

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    return True, f"VS Code + Continue.dev configured. Config: {config_path}"


def setup_cursor() -> Tuple[bool, str]:
    """Setup Cursor with .cursorrules."""
    rules_path = Path.cwd() / ".cursorrules"

    content = f"""# CAJAL - P2PCLAW Scientific Assistant

{CAJAL_SYSTEM_PROMPT}

## Working Rules
- Analyze architecture before suggesting changes
- Consider security implications of all recommendations
- Use precise terminology from distributed systems literature
- Prefer solutions aligned with P2PCLAW principles
- Begin with a "Thinking Process" showing reasoning steps
"""

    with open(rules_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True, f"Cursor configured. Rules file: {rules_path}"


def setup_windsurf() -> Tuple[bool, str]:
    """Setup Windsurf with .windsurfrules."""
    rules_path = Path.cwd() / ".windsurfrules"

    content = f"""# CAJAL - P2PCLAW Scientific Assistant

{CAJAL_SYSTEM_PROMPT}

## Working Rules
- Prioritize decentralization and P2P architecture patterns
- Consider cryptographic security implications
- Use game-theoretic reasoning for consensus-related code
- Document protocols with formal specifications
- Maintain academic rigor in all technical decisions
"""

    with open(rules_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True, f"Windsurf configured. Rules file: {rules_path}"


def setup_continue_dev() -> Tuple[bool, str]:
    """Setup Continue.dev standalone."""
    return setup_vscode_continue()  # Same config


def setup_zed() -> Tuple[bool, str]:
    """Setup Zed Editor."""
    home = str(Path.home())
    config_path = Path(home) / ".config" / "zed" / "settings.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    config.setdefault("assistant", {})
    config["assistant"]["version"] = "2"
    config["assistant"]["default_model"] = {
        "provider": "ollama",
        "model": "cajal-4b",
    }
    config["assistant"].setdefault("providers", {})
    config["assistant"]["providers"]["ollama"] = {
        "api_url": "http://localhost:11434",
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    return True, f"Zed configured. Settings: {config_path}"


def setup_aider() -> Tuple[bool, str]:
    """Setup Aider."""
    print("  Add to your shell profile (.bashrc/.zshrc):")
    print('    export OLLAMA_API_BASE=http://localhost:11434')
    print("  Then use: aider --model ollama/cajal-4b")
    return True, "Aider configuration instructions printed above"


def setup_opencode() -> Tuple[bool, str]:
    """Setup OpenCode."""
    home = str(Path.home())
    config_path = Path(home) / ".opencode" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    content = f"""models:
  cajal-4b:
    provider: ollama
    model: cajal-4b
    base_url: http://localhost:11434
    temperature: 0.7
    max_tokens: 4096

default_model: cajal-4b

system_prompt: |
  {CAJAL_SYSTEM_PROMPT}
"""

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True, f"OpenCode configured. Config: {config_path}"


def setup_lmstudio() -> Tuple[bool, str]:
    """Setup LM Studio."""
    return True, (
        "LM Studio: Load CAJAL-4B by importing the GGUF file. "
        "Download from: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW"
    )


def setup_open_webui() -> Tuple[bool, str]:
    """Setup Open WebUI."""
    return True, (
        "Open WebUI: CAJAL-4B should appear automatically in the model list "
        "when Ollama is running. If not, go to Admin Panel > Settings > Models "
        "and add 'cajal-4b'."
    )


def setup_jan() -> Tuple[bool, str]:
    """Setup Jan."""
    return True, (
        "Jan: Import CAJAL-4B GGUF from Settings > Models > Import Model. "
        "Download from: https://huggingface.co/Agnuxo/CAJAL-4B-P2PCLAW"
    )


def setup_codex_cli() -> Tuple[bool, str]:
    """Setup Codex CLI."""
    print("  Add to your shell profile (.bashrc/.zshrc):")
    print('    export OPENAI_BASE_URL=http://localhost:8765/v1')
    print('    export OPENAI_API_KEY=sk-cajal-local')
    print("  Then use: codex --model cajal-4b")
    return True, "Codex CLI configuration instructions printed above"


def check_all() -> List[Tuple[str, bool]]:
    """Check which platforms are installed."""
    results = []
    for key, info in PLATFORMS.items():
        installed = is_installed(info)
        results.append((info["name"], installed))
    return results


def setup_platform(platform_key: str) -> Tuple[bool, str]:
    """Setup a specific platform."""
    if platform_key not in PLATFORMS:
        return False, f"Unknown platform: {platform_key}"

    info = PLATFORMS[platform_key]
    print(f"\n  Setting up {info['name']}...")

    setup_fn_name = info.get("setup_fn")
    if setup_fn_name and setup_fn_name in globals():
        return globals()[setup_fn_name]()

    return False, f"No setup function for {platform_key}"


def main():
    parser = argparse.ArgumentParser(
        description="CAJAL Universal Setup - Auto-configure all platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cajal-setup.py              # Auto-detect and configure all
  python cajal-setup.py -p cursor    # Configure only Cursor
  python cajal-setup.py -p vscode    # Configure only VS Code
  python cajal-setup.py --list       # List supported platforms
  python cajal-setup.py --check      # Check what's installed
        """,
    )
    parser.add_argument(
        "--platform", "-p", help="Configure specific platform only"
    )
    parser.add_argument("--list", action="store_true", help="List supported platforms")
    parser.add_argument(
        "--check", action="store_true", help="Check which platforms are installed"
    )
    args = parser.parse_args()

    if args.list:
        print("\nSupported platforms:")
        print("=" * 50)
        for key, info in PLATFORMS.items():
            print(f"  {key:20s} - {info['name']}")
        print("=" * 50)
        return

    if args.check:
        print("\nChecking installed platforms:")
        print("=" * 50)
        results = check_all()
        for name, installed in results:
            status = "[OK] Installed" if installed else "[--] Not found"
            print(f"  {status:20s} {name}")
        print("=" * 50)
        return

    if args.platform:
        success, msg = setup_platform(args.platform)
        print(f"\n  {'[OK]' if success else '[FAIL]'} {msg}")
        return

    # Auto mode: check all and configure installed ones
    print("\n" + "=" * 56)
    print("  CAJAL Universal Setup")
    print("  Detecting and configuring all platforms...")
    print("=" * 56)

    results = check_all()
    configured = 0
    failed = 0

    for platform_key, (name, installed) in zip(PLATFORMS.keys(), results):
        if not installed:
            print(f"\n  [SKIP] {name} - not installed")
            continue

        success, msg = setup_platform(platform_key)
        if success:
            configured += 1
            print(f"  [OK] {msg}")
        else:
            failed += 1
            print(f"  [FAIL] {msg}")

    print("\n" + "=" * 56)
    print(f"  Setup complete: {configured} configured, {failed} failed")
    print("  Next: Run 'cajal status' to verify")
    print("=" * 56 + "\n")


if __name__ == "__main__":
    main()
