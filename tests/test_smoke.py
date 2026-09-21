"""Deterministic smoke tests for the local CAJAL package."""

import json

from cajal import CAJAL, __version__
from cajal import config
from cajal.cli import create_modelfile


def test_package_exports_and_ollama_configuration():
    client = CAJAL.from_ollama(host="http://127.0.0.1:11434", model="cajal-test")

    assert __version__ == "1.0.0"
    assert client.backend == "ollama"
    assert client.config == {
        "host": "http://127.0.0.1:11434",
        "model": "cajal-test",
    }


def test_config_round_trip_uses_defaults(tmp_path, monkeypatch):
    config_dir = tmp_path / ".cajal"
    config_file = config_dir / "config.json"
    monkeypatch.setattr(config, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config, "CONFIG_FILE", config_file)

    created = config.get_config()
    assert created["model"] == "cajal-4b"

    config.save_config({"model": "local-test"})
    loaded = config.get_config()
    assert loaded["model"] == "local-test"
    assert loaded["context_length"] == 4096
    assert json.loads(config_file.read_text(encoding="utf-8"))["model"] == "local-test"


def test_create_modelfile_is_valid_text():
    modelfile = create_modelfile()

    assert modelfile.startswith("FROM ./CAJAL-4B-f16.gguf")
    assert 'TEMPLATE """' in modelfile
    assert "PARAMETER num_ctx 4096" in modelfile


def test_server_health_and_openai_compatibility(monkeypatch):
    from cajal import server

    monkeypatch.setattr(
        server,
        "get_config",
        lambda: {"model": "cajal-test", "ollama_host": "http://127.0.0.1:11434"},
    )
    client = server.create_app().test_client()

    health = client.get("/health")
    models = client.get("/v1/models")
    completion = client.post("/v1/completions", json={"prompt": "hello"})

    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"
    assert models.get_json()["data"][0]["id"] == "cajal-4b"
    assert completion.get_json()["choices"][0]["text"] == "hello"

