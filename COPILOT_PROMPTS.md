# Microsoft Copilot prompts — InventoryHub final review

These prompts can be pasted into Microsoft Copilot Chat in VS Code. Open the **entire `InventoryHub_Final` solution** so Copilot has file context. The code is a reference implementation; check and test Copilot suggestions rather than accepting everything.

## Activity 1 — Generate and refine integration

> Inspect `ClientApp/Program.cs`, `ClientApp/Pages/FetchProducts.razor` and `ServerApp/Program.cs`. Explain how the Blazor WebAssembly client makes an HTTP GET against the Minimal API, which host and port each application uses, how JSON maps to Product/Category models, and whether the loading, empty and failure states are robust. Propose minimal code changes and explain each one.

## Activity 2 — Debug regressions

> Check for mistakes involving `/api/products` vs `/api/productlist`, missing CORS setup, malformed JSON, incorrect media types and timeouts. Inspect `ServerApp/Program.cs`, `ClientApp/Services/ProductService.cs`, and `ClientApp/Pages/FetchProducts.razor`. Propose safe changes that preserve permissive CORS ONLY for Development, explicit allowed origin for Production, specific exceptions and friendly UI messages. Provide a manual negative-test plan.

## Activity 3 — Typed nested JSON contract

> Compare `ServerApp/Models/`, `ClientApp/Models/`, `contracts/productlist.example.json` and `contracts/productlist.schema.json`. Ensure `GET /api/productlist` returns a camelCase JSON array whose objects include id, name, price, stock and nested category id/name. Check decimal price precision and strict client deserialization. Point out any ways the API and schema may drift apart and propose tests.

## Activity 4 — Reduce duplicate client requests

> Review `ClientApp/Services/ProductService.cs` for concurrency correctness, request coalescing, cache expiration, cancellation and exceptions. The Blazor client has an independent 15-second validated-data cache. Find any data races, stuck in-flight tasks, stale-cache risks, and paths that cache failed responses. Propose concrete improvements with justification and a browser Network tab test plan. Do not claim benchmarks without measurement.

## Activity 4 — Back-end output caching

> Review `ServerApp/Program.cs` against current ASP.NET Core 10 guidance for AddOutputCache, UseOutputCache and endpoint CacheOutput. Confirm that middleware ordering is UseRouting -> UseCors -> UseOutputCache, that output caching is limited to GET /api/productlist with a 30-second TTL, and that CORS works in Development while production has an explicit allowed origin. Suggest a cache invalidation strategy if a stock-update endpoint is added.

## Activity 4 — Performance and regression evidence

> Help me execute `scripts/smoke_test.py`, `scripts/benchmark_api.py`, `scripts/compare_benchmarks.py` and the tests in `PERFORMANCE.md`. Suggest a fair Activity 3 vs Activity 4 measurement procedure on the same machine: include first load, navigation under 15 seconds, 30-second server cache hits, warm-up requests, median/p95 latency and realistic uncertainty. Report only results actually measured in the terminal or DevTools.

## Activity 4 — Reflection and GitHub preparation

> Review `REFLECTION.md` as a DRAFT. Ask me which Copilot suggestions I actually used and which tests I ran; help me turn my REAL observations into a concise first-person reflection without making up Copilot interactions or performance results. Review `.gitignore`, README setup commands and the repository structure for GitHub peer review. Do not include credentials or generated `bin/` or `obj/` files.
