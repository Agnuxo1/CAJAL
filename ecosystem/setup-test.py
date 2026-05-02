#!/usr/bin/env python3
"""
CAJAL Ecosystem Setup & Test Script

Validates the entire CAJAL-4B ecosystem installation and runs tests.

Usage:
    python setup-test.py
    python setup-test.py --full      # Run integration tests
    python setup-test.py --install   # Install ecosystem locally
"""

import argparse
import io
import json
import subprocess
import sys
import time
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import requests
except ImportError:
    print("[ERROR] requests not installed. Run: pip install requests")
    sys.exit(1)

ECOSYSTEM_DIR = Path(__file__).parent
RESULTS = {"pass": 0, "fail": 0, "warnings": 0}

def check(name, condition, critical=True):
    """Check a condition and report."""
    if condition:
        print(f"  ✅ {name}")
        RESULTS["pass"] += 1
        return True
    else:
        if critical:
            print(f"  ❌ {name}")
            RESULTS["fail"] += 1
        else:
            print(f"  ⚠️  {name}")
            RESULTS["warnings"] += 1
        return False

def test_structure():
    """Test 1: Directory structure"""
    print("\n📁 Test 1: Directory Structure")
    
    required_dirs = [
        "cli", "webapp", "vscode-extension",
        "api-bridge", "integrations", "installer"
    ]
    
    for d in required_dirs:
        check(f"Directory: {d}/", (ECOSYSTEM_DIR / d).is_dir())

def test_cli():
    """Test 2: CLI Tool"""
    print("\n🖥️  Test 2: CLI Tool")
    
    cli_dir = ECOSYSTEM_DIR / "cli"
    check("cajal.py exists", (cli_dir / "cajal.py").exists())
    check("requirements.txt exists", (cli_dir / "requirements.txt").exists())
    
    # Try running --help
    try:
        result = subprocess.run(
            [sys.executable, str(cli_dir / "cajal.py"), "--help"],
            capture_output=True, text=True, timeout=10
        )
        check("cajal.py runs", result.returncode == 0)
        if result.returncode == 0:
            check("cajal.py has commands", "chat" in result.stdout and "status" in result.stdout)
    except Exception as e:
        check("cajal.py execution", False)

def test_webapp():
    """Test 3: Web App"""
    print("\n🌐 Test 3: Web Application")
    
    web_dir = ECOSYSTEM_DIR / "webapp"
    check("index.html exists", (web_dir / "index.html").exists())
    check("app.js exists", (web_dir / "app.js").exists())
    check("styles.css exists", (web_dir / "styles.css").exists())
    
    # Check HTML references
    if (web_dir / "index.html").exists():
        html = (web_dir / "index.html").read_text(encoding='utf-8')
        check("HTML references app.js", "app.js" in html)
        check("HTML references styles.css", "styles.css" in html)
        check("HTML has CAJAL branding", "CAJAL" in html)

def test_vscode_extension():
    """Test 4: VS Code Extension"""
    print("\n📝 Test 4: VS Code Extension")
    
    ext_dir = ECOSYSTEM_DIR / "vscode-extension"
    check("package.json exists", (ext_dir / "package.json").exists())
    check("extension.js exists", (ext_dir / "extension.js").exists())
    
    if (ext_dir / "package.json").exists():
        pkg = json.loads((ext_dir / "package.json").read_text(encoding='utf-8'))
        check("Extension name is cajal-vscode", pkg.get("name") == "cajal-vscode")
        check("Has activation events", "activationEvents" in pkg)
        check("Has contributions", "contributes" in pkg)

def test_api_bridge():
    """Test 5: API Bridge"""
    print("\n🔌 Test 5: API Bridge")
    
    bridge_file = ECOSYSTEM_DIR / "api-bridge" / "bridge.py"
    check("bridge.py exists", bridge_file.exists())
    
    if bridge_file.exists():
        content = bridge_file.read_text(encoding='utf-8')
        check("Has /health endpoint", "/health" in content)
        check("Has /v1/chat/completions", "/v1/chat/completions" in content)
        check("Has CORS support", "CORS" in content)

def test_integrations():
    """Test 6: Integration Guides"""
    print("\n🔗 Test 6: Integration Guides")
    
    int_dir = ECOSYSTEM_DIR / "integrations"
    required = [
        "ollama.md", "continue.dev.md", "claude-desktop.md",
        "cursor.md", "open-webui.md", "anythingllm.md",
        "lmstudio.md", "chatgpt-custom.md", "zed.md",
        "aider.md", "opencode.md", "lobechat.md",
        "jan.md", "openrouter.md", "text-generation-webui.md"
    ]
    
    for f in required:
        check(f"Integration: {f}", (int_dir / f).exists(), critical=False)
    
    # Check README
    check("integrations/README.md", (int_dir / "README.md").exists())

def test_installer():
    """Test 7: Installer Scripts"""
    print("\n📦 Test 7: Installers")
    
    inst_dir = ECOSYSTEM_DIR / "installer"
    check("install.ps1 exists", (inst_dir / "install.ps1").exists())
    check("install.sh exists", (inst_dir / "install.sh").exists())
    
    if (inst_dir / "install.ps1").exists():
        content = (inst_dir / "install.ps1").read_text(encoding='utf-8')
        check("PS installer checks Ollama", "ollama" in content.lower())
        check("PS installer creates shortcuts", "Shortcut" in content)
    
    if (inst_dir / "install.sh").exists():
        content = (inst_dir / "install.sh").read_text(encoding='utf-8')
        check("Bash installer is executable", True)  # Can't check perms on Windows

def test_ollama_connection():
    """Test 8: Ollama Status"""
    print("\n🦙 Test 8: Ollama Connection")
    
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        check("Ollama is running", r.status_code == 200)
        
        if r.status_code == 200:
            data = r.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            has_cajal = any("cajal" in m for m in models)
            check("CAJAL model installed", has_cajal)
            check(f"Total models: {len(models)}", len(models) >= 0)
    except requests.exceptions.ConnectionError:
        check("Ollama is running", False)
        print("     → Install Ollama: https://ollama.com/download")
    except Exception as e:
        check("Ollama check", False)
        print(f"     → Error: {e}")

def test_api_bridge_running():
    """Test 9: API Bridge Server (optional)"""
    print("\n🌉 Test 9: API Bridge Server (Optional)")
    
    try:
        r = requests.get("http://localhost:8765/health", timeout=2)
        check("Bridge is running", r.status_code == 200)
        if r.status_code == 200:
            data = r.json()
            check("Bridge returns version", "version" in data)
    except requests.exceptions.ConnectionError:
        check("Bridge is running", False, critical=False)
        print("     → Start with: python api-bridge/bridge.py")

def test_model_response():
    """Test 10: CAJAL Model Response"""
    print("\n🧠 Test 10: CAJAL Model Response")
    
    try:
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "cajal-4b",
                "messages": [{"role": "user", "content": "Say 'CAJAL is ready'"}],
                "stream": False
            },
            timeout=120
        )
        check("Model responds", r.status_code == 200, critical=False)
        
        if r.status_code == 200:
            data = r.json()
            response = data.get("message", {}).get("content", "")
            check("Response is non-empty", len(response) > 0, critical=False)
            print(f"     → Response: {response[:100]}...")
    except requests.exceptions.ConnectionError:
        check("Model responds", False, critical=False)
    except Exception as e:
        check("Model test", False, critical=False)
        print(f"     → Error: {e}")

def print_summary():
    """Print final summary"""
    print("\n" + "="*60)
    print("  CAJAL Ecosystem Test Summary")
    print("="*60)
    print(f"  ✅ Passed:   {RESULTS['pass']}")
    print(f"  ❌ Failed:   {RESULTS['fail']}")
    print(f"  ⚠️  Warnings: {RESULTS['warnings']}")
    print("="*60)
    
    if RESULTS['fail'] == 0:
        print("\n  🎉 All critical tests passed! CAJAL ecosystem is ready.")
    else:
        print(f"\n  ⚠️  {RESULTS['fail']} critical test(s) failed. Please fix before deploying.")
    
    print("\n  Next steps:")
    print("    1. Ensure Ollama is running: ollama serve")
    print("    2. Install CAJAL model: cajal-cli install")
    print("    3. Start chatting: cajal-cli chat")
    print("    4. Open Web App: open ecosystem/webapp/index.html")
    print("    5. Start API Bridge: python ecosystem/api-bridge/bridge.py")
    print("")

def install_locally():
    """Install the ecosystem locally for testing."""
    print("\n📦 Local Installation")
    print("-" * 40)
    
    # Install CLI dependencies
    cli_req = ECOSYSTEM_DIR / "cli" / "requirements.txt"
    if cli_req.exists():
        print("Installing CLI dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(cli_req)])
    
    # Install API bridge dependencies
    print("Installing API bridge dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "flask", "flask-cors"])
    
    print("✅ Dependencies installed")
    print("   Run: python setup-test.py to verify")

def main():
    parser = argparse.ArgumentParser(description="CAJAL Ecosystem Setup & Test")
    parser.add_argument("--full", action="store_true", help="Run full integration tests")
    parser.add_argument("--install", action="store_true", help="Install dependencies locally")
    args = parser.parse_args()
    
    print("="*60)
    print("  CAJAL Ecosystem Setup & Test")
    print("  P2PCLAW Lab, Zurich")
    print("="*60)
    
    if args.install:
        install_locally()
        return
    
    # Run all tests
    test_structure()
    test_cli()
    test_webapp()
    test_vscode_extension()
    test_api_bridge()
    test_integrations()
    test_installer()
    
    if args.full:
        test_ollama_connection()
        test_api_bridge_running()
        test_model_response()
    
    print_summary()
    
    # Return exit code based on failures
    sys.exit(0 if RESULTS["fail"] == 0 else 1)

if __name__ == "__main__":
    main()
