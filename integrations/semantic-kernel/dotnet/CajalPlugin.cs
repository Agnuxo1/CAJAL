using System.ComponentModel;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.SemanticKernel;

namespace Cajal.SemanticKernel;

/// <summary>Native community plugin for the installable CAJAL local chat server.</summary>
public sealed class CajalPlugin
{
    private readonly HttpClient _http;
    private readonly Uri _server;
    private readonly string _model;

    public CajalPlugin(HttpClient http, Uri server, string model)
    {
        ArgumentNullException.ThrowIfNull(http);
        ArgumentNullException.ThrowIfNull(server);
        ArgumentException.ThrowIfNullOrWhiteSpace(model);
        if (!server.IsAbsoluteUri || !server.IsLoopback ||
            server.Scheme is not ("http" or "https") || server.UserInfo.Length != 0)
        {
            throw new ArgumentException("CAJAL server must be a loopback HTTP(S) URL without credentials.", nameof(server));
        }
        _http = http;
        _server = server;
        _model = model;
    }

    [KernelFunction("ask_local")]
    [Description("Ask the local CAJAL/Ollama model. Output is generated text, not verified facts or citations.")]
    public async Task<string> AskAsync(
        [Description("Question or drafting instructions, with evidence supplied by the caller.")] string prompt,
        CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(prompt);
        var body = new
        {
            model = _model,
            stream = false,
            messages = new[]
            {
                new { role = "system", content = "Distinguish supplied evidence from generated hypotheses. Do not invent results, sources or verification." },
                new { role = "user", content = prompt }
            }
        };
        using var response = await _http.PostAsJsonAsync(new Uri(_server, "/v1/chat/completions"), body, cancellationToken);
        response.EnsureSuccessStatusCode();
        await using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
        using var json = await JsonDocument.ParseAsync(stream, cancellationToken: cancellationToken);
        var choices = json.RootElement.GetProperty("choices");
        if (choices.ValueKind != JsonValueKind.Array || choices.GetArrayLength() == 0)
            throw new InvalidDataException("CAJAL returned no completion choices.");
        var content = choices[0].GetProperty("message").GetProperty("content");
        if (content.ValueKind != JsonValueKind.String || string.IsNullOrWhiteSpace(content.GetString()))
            throw new InvalidDataException("CAJAL returned no assistant text.");
        return content.GetString()!;
    }

    [KernelFunction("health")]
    [Description("Read the local CAJAL server health metadata; this does not prove that a model can perform inference.")]
    public async Task<string> HealthAsync(CancellationToken cancellationToken = default)
    {
        using var response = await _http.GetAsync(new Uri(_server, "/health"), cancellationToken);
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync(cancellationToken);
        using var json = JsonDocument.Parse(content);
        if (json.RootElement.ValueKind != JsonValueKind.Object)
            throw new InvalidDataException("CAJAL returned invalid health metadata.");
        return content;
    }
}
