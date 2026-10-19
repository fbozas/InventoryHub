using System.Globalization;
using ServerApp.Models;

var builder = WebApplication.CreateBuilder(args);

// Activity 2: retain CORS. Activity 4 Copilot review checkpoint:
// cache middleware must run AFTER CORS to preserve cross-origin behavior.
builder.Services.AddCors();

// Activity 4: ASP.NET Core output caching saves repeated JSON serialization
// and endpoint execution. This is server-side caching, not browser caching.
const string productCachePolicy = "ProductList30Seconds";
builder.Services.AddOutputCache(options =>
    options.AddPolicy(productCachePolicy, policy =>
        policy.Expire(TimeSpan.FromSeconds(30))));

var app = builder.Build();
app.UseRouting();

if (app.Environment.IsDevelopment())
{
    // Activity 2: allow the separate Blazor development origin.
    // Never use AllowAnyOrigin() for a deployed application.
    app.UseCors(policy => policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader());
}
else
{
    var allowedOrigin = app.Configuration["AllowedClientOrigin"];
    if (string.IsNullOrWhiteSpace(allowedOrigin))
    {
        throw new InvalidOperationException(
            "Set AllowedClientOrigin to the exact trusted Blazor origin before deploying.");
    }

    app.UseCors(policy => policy.WithOrigins(allowedOrigin).AllowAnyMethod().AllowAnyHeader());
}

// Middleware ordering matters: UseRouting -> UseCors -> UseOutputCache.
app.UseOutputCache();

// Activity 3: keep the established camelCase JSON contract and nested category.
// Inventory is sample read-only data, so caching for 30 seconds is appropriate.
// In a writable inventory application, invalidate this cache when stock changes.
var products = new ProductDto[]
{
    new(1, "Laptop", 1200.50m, 25, new CategoryDto(101, "Electronics")),
    new(2, "Headphones", 50.00m, 100, new CategoryDto(102, "Accessories"))
};

// The generation counter is a tiny demonstration diagnostic: it increments
// ONLY when the endpoint executes (not when output cache serves a response).
// Compare this header across consecutive GETs to verify server cache hits.
long generationCount = 0;

app.MapGet("/api/productlist", (HttpContext context) =>
{
    var generation = Interlocked.Increment(ref generationCount);
    context.Response.Headers["X-InventoryHub-Generation"] =
        generation.ToString(CultureInfo.InvariantCulture);
    return Results.Ok(products);
})
.CacheOutput(productCachePolicy);

app.Run();
