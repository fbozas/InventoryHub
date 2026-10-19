using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using ClientApp.Models;

namespace ClientApp.Services;

/// <summary>
/// Fetches validated products with a short-lived in-memory cache and a shared
/// in-flight request. This keeps repeated Blazor navigations from re-fetching
/// the same products while preserving the Activity 2/3 JSON safety checks.
/// </summary>
public sealed class ProductService(HttpClient http)
{
    private const string ProductsEndpoint = "api/productlist";
    private static readonly TimeSpan ClientCacheDuration = TimeSpan.FromSeconds(15);
    private static readonly TimeSpan RequestTimeout = TimeSpan.FromSeconds(10);
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
    {
        NumberHandling = JsonNumberHandling.Strict,
        AllowDuplicateProperties = false,
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
    };

    private readonly object _sync = new();
    private Product[]? _cachedProducts;
    private DateTimeOffset _validUntilUtc;
    private Task<Product[]>? _inFlight;

    /// <param name="forceRefresh">Bypasses the local cache for an explicit user refresh.</param>
    /// <remarks>
    /// Activity 4 Copilot review checkpoint: only successful, validated results
    /// are cached. Concurrent callers await one fetch rather than duplicating it.
    /// Cancelling a component's wait must not cancel another caller's fetch.
    /// </remarks>
    public Task<Product[]> GetProductsAsync(
        bool forceRefresh = false,
        CancellationToken cancellationToken = default)
    {
        Task<Product[]> pending;
        lock (_sync)
        {
            if (!forceRefresh && _cachedProducts is not null &&
                DateTimeOffset.UtcNow < _validUntilUtc)
            {
                return Task.FromResult(_cachedProducts);
            }

            _inFlight ??= FetchAndCacheAsync();
            pending = _inFlight;
        }

        return pending.WaitAsync(cancellationToken);
    }

    private async Task<Product[]> FetchAndCacheAsync()
    {
        try
        {
            // The shared fetch has its own timeout; caller cancellation only
            // stops that component waiting (other consumers may still need it).
            using var timeout = new CancellationTokenSource(RequestTimeout);
            using var response = await http.GetAsync(ProductsEndpoint, timeout.Token);
            response.EnsureSuccessStatusCode();

            var mediaType = response.Content.Headers.ContentType?.MediaType;
            if (mediaType is null ||
                !(mediaType.Equals("application/json", StringComparison.OrdinalIgnoreCase) ||
                  mediaType.EndsWith("+json", StringComparison.OrdinalIgnoreCase)))
            {
                throw new JsonException("The server did not return JSON.");
            }

            // Stream deserialization avoids allocating an intermediate JSON string.
            // This is an Activity 4 optimization over Activity 3's ReadAsStringAsync.
            var products = await response.Content.ReadFromJsonAsync<Product[]>(
                JsonOptions, timeout.Token);
            if (products is null || products.Any(p =>
                    p is null ||
                    p.Id <= 0 ||
                    string.IsNullOrWhiteSpace(p.Name) ||
                    p.Price < 0 ||
                    p.Stock < 0 ||
                    p.Category is null ||
                    p.Category.Id <= 0 ||
                    string.IsNullOrWhiteSpace(p.Category.Name)))
            {
                throw new JsonException("The API returned invalid product records.");
            }

            lock (_sync)
            {
                _cachedProducts = products;
                _validUntilUtc = DateTimeOffset.UtcNow.Add(ClientCacheDuration);
            }

            return products;
        }
        finally
        {
            // Errors aren't cached: the next visit can retry the server.
            lock (_sync)
            {
                _inFlight = null;
            }
        }
    }
}
