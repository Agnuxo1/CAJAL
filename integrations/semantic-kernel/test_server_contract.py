"""Real HTTP: .NET Kernel plugin -> actual CAJAL Flask app -> mocked model backend."""
import os
from pathlib import Path
import subprocess
import threading
from unittest.mock import patch

from werkzeug.serving import make_server
from cajal.server import create_app

root = Path(__file__).resolve().parent
calls = []

class Backend:
    def chat(self, **kwargs):
        calls.append(kwargs)
        return "CAJAL HTTP contract fixture; no model inference"

def backend_factory(**kwargs):
    calls.append(kwargs)
    return Backend()

with patch("cajal.server.CAJAL.from_ollama", side_effect=backend_factory):
    server = make_server("127.0.0.1", 0, create_app())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        env = dict(os.environ, CAJAL_MODEL="contract-fixture", CAJAL_SERVER=f"http://127.0.0.1:{server.server_port}")
        result = subprocess.run(["dotnet", str(root / "dotnet/Example/bin/Debug/net9.0/Example.dll"),
                                 "Evidence:12 observations. Summarize."], env=env, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stderr
        assert "CAJAL HTTP contract fixture; no model inference" in result.stdout
        assert calls[0]["model"] == "contract-fixture"
        assert calls[1]["message"] == "Evidence:12 observations. Summarize."
        assert "Do not invent" in calls[1]["system"]
        print("PASS: .NET Kernel -> real HTTP -> CAJAL Flask routing/model/prompt -> mocked backend; no inference.")
    finally:
        server.shutdown(); thread.join(timeout=5); server.server_close()
