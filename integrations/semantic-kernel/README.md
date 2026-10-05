# CAJAL community plugin for Semantic Kernel (.NET)

Native `KernelFunction` plugin for CAJAL's installable local chat server, using
Semantic Kernel Core **1.80.1** and .NET 9. The plugin exposes `ask_local` and
`health`; it makes no changes to Semantic Kernel core. It does not generate
verified papers, check references, run experiments, or perform peer review.
Model responses remain generated text requiring human verification.

## Run

Start Ollama separately with an already installed model, then:

```sh
pip install 'cajal[server]'
cajal-server --host 127.0.0.1 --port 8765
# In another terminal, set CAJAL_MODEL to the name of your installed Ollama model.
dotnet run --project integrations/semantic-kernel/dotnet/Example -- "Summarize these supplied observations..."
```

The plugin only permits loopback HTTP(S) endpoints, sends the model name and
caller prompt to `/v1/chat/completions` with `stream:false`, propagates HTTP and
cancellation errors, and rejects empty completions. The example disables
redirects and has a five-minute timeout. No hosted API credentials are needed.
The Python server's own `ollama_host` configuration controls the inference
destination; keep that set to loopback for a fully local setup. Health metadata
does not establish that model inference works. No models are downloaded by this
integration, and no arbitrary code or autonomous tool loop is executed.

## Regression checks

```sh
dotnet run --project integrations/semantic-kernel/dotnet/Smoke
dotnet build integrations/semantic-kernel/dotnet/Example
PYTHONPATH=src python integrations/semantic-kernel/test_server_contract.py
```

Smoke uses the **real SK SDK** for plugin discovery and `Kernel.InvokeAsync`,
with a mocked HTTP transport: it covers request/model/prompt mapping, errors,
malformed responses, cancellation and loopback scope. This is contract
validation, not a model-quality or real-inference benchmark.

The server-contract check also runs the built .NET example against the actual
CAJAL Flask app over loopback HTTP, with a mocked model backend. It checks the
request through both implementations; it does not download or run model weights.

Native-plugin API: https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/adding-native-plugins
