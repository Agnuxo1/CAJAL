using Cajal.SemanticKernel;
using Microsoft.SemanticKernel;

var model = Environment.GetEnvironmentVariable("CAJAL_MODEL") ?? "cajal-4b";
var server = new Uri(Environment.GetEnvironmentVariable("CAJAL_SERVER") ?? "http://127.0.0.1:8765");
using var plugin = new CajalPlugin(server, model);
var kernel = Kernel.CreateBuilder().Build();
kernel.Plugins.AddFromObject(plugin, "cajal");
var result = await kernel.InvokeAsync("cajal", "ask_local", new KernelArguments
{
    ["prompt"] = args.Length == 0 ? "Explain the difference between a hypothesis and an observed result." : string.Join(" ", args)
});
Console.WriteLine(result.GetValue<string>());
