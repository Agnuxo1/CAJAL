using System.Net;
using System.Text;
using System.Text.Json;
using Cajal.SemanticKernel;
using Microsoft.SemanticKernel;

var handler = new FakeServer();
using var http = new HttpClient(handler);
var plugin = new CajalPlugin(http, new Uri("http://127.0.0.1:8765"), "fixture-model");
var kernel = Kernel.CreateBuilder().Build();
kernel.Plugins.AddFromObject(plugin, "cajal");
Check(kernel.Plugins["cajal"].Count() == 2, "plugin discovery");
var answer = await kernel.InvokeAsync("cajal", "ask_local", new KernelArguments { ["prompt"] = "Evidence: 12 samples. Summarize without inventing findings." });
Check(answer.GetValue<string>() == "Fixture response (not real inference)", "Kernel invocation");
Check(handler.LastUri?.AbsolutePath == "/v1/chat/completions", "correct endpoint");
using (var json = JsonDocument.Parse(handler.LastBody!))
{
    Check(json.RootElement.GetProperty("model").GetString() == "fixture-model", "model forwarding");
    Check(!json.RootElement.GetProperty("stream").GetBoolean(), "non-streaming request");
    Check(json.RootElement.GetProperty("messages")[1].GetProperty("content").GetString()!.StartsWith("Evidence:"), "caller evidence");
}
var health = await kernel.InvokeAsync("cajal", "health");
Check(health.GetValue<string>()!.Contains("fixture-model"), "health invocation");
await Expect<ArgumentException>(() => plugin.AskAsync(" "), "empty prompt rejected");
handler.Status = HttpStatusCode.ServiceUnavailable;
await Expect<HttpRequestException>(() => plugin.AskAsync("test"), "HTTP error propagated");
handler.Status = HttpStatusCode.OK;
foreach (var invalid in new[] {"not-json", "{\"choices\":[]}", "{\"choices\":[{\"message\":{\"content\":null}}]}"})
{
    handler.Reply = invalid;
    var failed = false;
    try { await plugin.AskAsync("test"); }
    catch (Exception ex) when (ex is JsonException or InvalidDataException) { failed = true; }
    Check(failed, "malformed/empty output rejected");
}
handler.Reply = FakeServer.GoodReply;
using var canceled = new CancellationTokenSource(); canceled.Cancel();
await Expect<OperationCanceledException>(() => plugin.AskAsync("test", canceled.Token), "cancellation propagated");
foreach (var uri in new[] { "https://example.com", "http://user:pass@localhost", "file:///tmp/server" })
{
    var failed = false;
    try { _ = new CajalPlugin(http, new Uri(uri), "fixture-model"); }
    catch (ArgumentException) { failed = true; }
    Check(failed, "remote/credentialed server rejected");
}
Console.WriteLine("PASS: real SK discovery/invocation, contract, errors, malformed output, cancellation and loopback scope. Transport is mocked; no model inference.");

static void Check(bool condition, string message) { if (!condition) throw new Exception("FAIL: " + message); }
static async Task Expect<T>(Func<Task<string>> action, string message) where T : Exception
{
    try { await action(); }
    catch (T) { return; }
    throw new Exception("FAIL: " + message);
}
sealed class FakeServer : HttpMessageHandler
{
    public const string GoodReply = "{\"choices\":[{\"message\":{\"content\":\"Fixture response (not real inference)\"}}]}";
    public string Reply = GoodReply;
    public HttpStatusCode Status = HttpStatusCode.OK;
    public Uri? LastUri;
    public string? LastBody;
    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken token)
    {
        token.ThrowIfCancellationRequested();
        LastUri = request.RequestUri;
        LastBody = request.Content is null ? null : await request.Content.ReadAsStringAsync(token);
        return new HttpResponseMessage(Status) { Content = new StringContent(request.RequestUri!.AbsolutePath == "/health" ? "{\"status\":\"ok\",\"model\":\"fixture-model\"}" : Reply, Encoding.UTF8, "application/json") };
    }
}
