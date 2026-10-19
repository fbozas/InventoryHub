# InventoryHub — Changes across Activities 1–4

| Activity | Key changes | Current state |
|---|---|---|
| 1: Integration | Blazor component, injected HttpClient, Minimal API GET products | Preserved and refactored into `ProductService` |
| 2: Debugging | Correct `/api/productlist` route, CORS middleware, timeout/HTTP/JSON error handling | Preserved; CORS before OutputCache |
| 3: JSON | Product/category typed records, strict JSON validation, schema and Postman tests | Preserved; nested category is displayed |
| 4: Performance | Scoped cached `ProductService`, 15s client TTL, coalesced concurrent fetches, streaming JSON deserialization, 30s server OutputCache, explicit refresh and disposal handling | Implemented; needs local .NET/browser testing |

## Activity 4 code review checkpoints

- `ClientApp/Program.cs`: registers a scoped client cache service.
- `ClientApp/Services/ProductService.cs`: request deduplication; short TTL; strict JSON validation; avoid caching failed responses.
- `ClientApp/Pages/FetchProducts.razor`: no automatic polling; refresh/error/cancellation UI.
- `ServerApp/Program.cs`: CORS first, then output caching; exactly one endpoint with typed DTOs; per-generation diagnostic.
- `scripts/smoke_test.py`: development live JSON/CORS plus warm output cache check.
- `scripts/benchmark_api.py`: client-observed baseline/final timings; `scripts/compare_benchmarks.py` computes changes.
- `PERFORMANCE.md`: baseline vs optimized test steps and fill-in measurement template.
- `REFLECTION.md`: transparent Copilot workflow reflection draft.

## Deployment caveat

GitHub repository publishing is separate from deploying live front-end/API hosting. Before public deployment, configure HTTPS, `AllowedClientOrigin`, and the Blazor API URL; review expiry/invalidation of inventory data.
