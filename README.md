# InventoryHub — Final Capstone (Activities 1–4)

**InventoryHub** is a two-process **.NET 10** demonstration of Blazor WebAssembly communicating with an ASP.NET Core Minimal API. It consolidates the four activities: integration, route/CORS/JSON debugging, nested JSON contracts, and performance optimization.

> **Verification status:** The provided source and offline Python contract/source tests can be tested without .NET. The authoring environment does not have the .NET SDK or a running browser; **build, live integration, Postman and performance measurements must be executed locally before submission**. No benchmarks or Microsoft Copilot sessions have been fabricated.

## Architecture

```text
Browser / ClientApp (http://localhost:5150)
  Pages/FetchProducts.razor
     -> scoped ProductService (15-second validated-result cache + in-flight de-dup)
     -> HttpClient GET http://localhost:5199/api/productlist
ServerApp (ASP.NET Core Minimal API)
  CORS middleware -> OutputCache middleware (30-second server-side cache)
     -> typed ProductDto + nested CategoryDto -> JSON (camelCase)
```

The API returns a top-level array with `id`, `name`, `price`, `stock` and `category` (which includes `id` and `name`). Prices are `decimal` in C#. The Blazor client strictly validates fields and data types and displays price, stock, and category. It shows friendly errors for API failures, non-JSON responses, invalid JSON, and timeouts. The Refresh button bypasses **only the 15-second client cache**; the server cache may still return its latest response within 30 seconds.

## Project contents

| Path | Purpose |
|---|---|
| `FullStackSolution.sln` | Solution for both C# projects |
| `ServerApp/Program.cs` | CORS, output cache, API endpoint and cache diagnostics |
| `ServerApp/Models/` | Typed Product and Category response DTOs |
| `ClientApp/Pages/FetchProducts.razor` | Product UI, error states, explicit refresh, cancellation on disposal |
| `ClientApp/Services/ProductService.cs` | Shared in-flight HTTP request, 15s cache, strict validation |
| `ClientApp/Models/` | Strict client product/category contract |
| `contracts/` | Example JSON plus JSON Schema Draft 2020-12 |
| `scripts/` | Offline contract tests, live smoke tests, benchmark and comparison CLI |
| `postman/InventoryHub.Final.postman_collection.json` | JSON/CORS/output-cache verification |
| `PERFORMANCE.md` | Reproducible benchmark instructions and results template |
| `REFLECTION.md` | AI/Copilot workflow reflection; includes disclosure on actual tool usage |
| `COPILOT_PROMPTS.md` | Prompts for reviewing/generating the four-activity code with Copilot |
| `CHANGES.md` | Traceability between Activities 1–4 |

## Prerequisites

- **.NET 10 SDK** (`dotnet --version`), VS Code + C# Dev Kit recommended.
- Python 3.9+ for offline tests and live benchmarks (no extra dependencies).
- Optional: Postman and Microsoft Copilot in VS Code for the required AI-assistance workflow.

## Build and launch

From this extracted project directory:

```bash
dotnet restore FullStackSolution.sln
dotnet build FullStackSolution.sln
```

Open two terminals in the project root:

```bash
# Terminal A
dotnet run --project ServerApp --launch-profile http
```

```bash
# Terminal B
dotnet run --project ClientApp --launch-profile http
```

- API: **http://localhost:5199/api/productlist**
- UI: **http://localhost:5150/fetchproducts**

Expected data:

| Product | Price | Stock | Category |
|---|---:|---:|---|
| Laptop | $1,200.50 | 25 | Electronics (101) |
| Headphones | $50.00 | 100 | Accessories (102) |

The API base URL is in `ClientApp/wwwroot/appsettings.json`. If you change the API port, update that value, restart the client, and check the browser's Network tab.

## Run all available tests

### Offline validation (does not need the server)

```bash
python scripts/validate_contract.py contracts/productlist.example.json
python -m unittest discover -s scripts -p 'test_*.py' -v
```

The offline tests validate the JSON contract, reject malformed/invalid nested data, check benchmark calculations, and check the presence of key integration and caching configuration. These tests are **not** a C# compiler or browser substitute.

### Integration (requires the running server in Development)

```bash
python scripts/smoke_test.py
```

Checks `GET /api/productlist`, strict JSON shape, expected data, Development CORS preflight, 404 on obsolete `/api/products`, and the output-cache generation header. The last two quick GETs should have the same `X-InventoryHub-Generation` because they use the same cached response for up to 30 seconds; if run exactly across a cache-expiry boundary, repeat the test.

### Postman

1. Import `postman/InventoryHub.Final.postman_collection.json`.
2. Start ServerApp in Development mode; collection variable `apiBaseUrl` defaults to `http://localhost:5199`.
3. Run the collection **in order and promptly**. It validates status, content type, nested JSON, Development CORS, preflight and two consecutive requests with the same generation header.
4. Browser: inspect DevTools **Network** and **Console** at `/fetchproducts`. Successful requests should be HTTP 200 JSON without CORS/deserialization errors. Navigate away and back within 15 seconds: expected **zero additional GETs** (client cache). After the cache expires, a new navigation fetches again; use the Refresh button for a manual request.

### Negative testing

Temporarily alter the API to return an object missing `category` or bad JSON, restart the server and reload the UI. Expect the friendly invalid product data message, rather than a broken page. Restore the valid backend after testing. Server output cache can hide temporary changes until expiry, so restarting the backend is useful for this test.

## Performance optimization

The final app avoids repeated API calls on short navigations by caching **only successful and validated results** in `ProductService` (15s), coalesces simultaneous requests into one fetch, streams JSON deserialization without an intermediate string, and lets ASP.NET Core output caching serve previously generated API responses (30s). `X-InventoryHub-Generation` is a demo diagnostic that changes when the endpoint re-runs and stays unchanged on server cache hits. Cache lifetimes are deliberately small to limit inventory staleness; when adding write endpoints, **invalidate server and client caches on updates**. For multiple server instances, the default in-process output cache isn't shared between instances; use a distributed output cache store if that is required.

See **[PERFORMANCE.md](PERFORMANCE.md)** for baseline-vs-optimized measurements. These do not have prefilled performance numbers: you will record real outputs locally. Benchmarks of a tiny two-item mock API may show little or no latency gain even when reducing backend executions; request count and endpoint generation count are more meaningful evidence.

## Deploy to GitHub for review

From the project root after local verification:

```bash
git init
git add .
git commit -m "Complete InventoryHub full-stack capstone"
git branch -M main
# Create an empty GitHub repository named InventoryHub in your account first.
git remote add origin https://github.com/YOUR_USERNAME/InventoryHub.git
git push -u origin main
```

Do not commit secrets or publish `bin/` or `obj/` (excluded via `.gitignore`). **Publishing source to GitHub is not hosting the running app.** For actual production web deployment: publish both projects to hosting, use **HTTPS**, change the client's `ApiBaseUrl` to your hosted server URL, set `AllowedClientOrigin` in ServerApp to the exact hosted Blazor origin, and review caching/privacy and any authentication requirements. The base sample is a public read-only demo.

## Microsoft Copilot and integrity

There are code comments marking AI review checkpoints and prompts in [`COPILOT_PROMPTS.md`](COPILOT_PROMPTS.md). The code is provided as a working **reference implementation** to review with Copilot; this authoring session did not directly execute Microsoft Copilot. **Run the prompts with Copilot and adapt [`REFLECTION.md`](REFLECTION.md) with your actual experience before presenting it as a first-person report.**

Microsoft references:
- [ASP.NET Core output caching](https://learn.microsoft.com/en-us/aspnet/core/performance/caching/output?view=aspnetcore-10.0)
- [CORS in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/security/cors?view=aspnetcore-10.0)
- [Call an API from Blazor](https://learn.microsoft.com/en-us/aspnet/core/blazor/call-web-api?view=aspnetcore-10.0)
