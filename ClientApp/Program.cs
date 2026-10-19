using ClientApp;
using ClientApp.Services;
using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;

var builder = WebAssemblyHostBuilder.CreateDefault(args);

builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

var apiBaseUrl = builder.Configuration["ApiBaseUrl"]
    ?? throw new InvalidOperationException("ApiBaseUrl is missing from wwwroot/appsettings.json.");

// The API is hosted separately from this Blazor WebAssembly application.
builder.Services.AddScoped(_ => new HttpClient
{
    BaseAddress = new Uri(apiBaseUrl, UriKind.Absolute)
});

// Activity 4: a scoped service shares one cached result and in-flight request
// across components during the Blazor WebAssembly application session.
builder.Services.AddScoped<ProductService>();

await builder.Build().RunAsync();
