# InventoryHub — Performance verification (Activity 4)

## Design and expected behavior

| Scenario | Activity 3 (before) | Activity 4 (after) |
|---|---|---|
| Initial entry to product page | 1 GET | 1 GET |
| Navigate away/back within 15 seconds | 1 new GET | **0 new GETs**, use client cache |
| Several components ask for products simultaneously | Typically multiple GETs | **1 shared in-flight GET** |
| Multiple GETs reach server within 30 seconds | Endpoint runs on each | Output cache normally reuses one endpoint response |
| Click manual Refresh | Not implemented | New client request; server cache may still hit |
| Invalid JSON / HTTP failure | Friendly error, no data | Friendly error, no data; bad data is not client cached |

These are design expectations, **not observed measurements**. Browser/component, CORS, and network testing on the target machine are required to confirm them.

## A. Measure browser network requests

1. Run Activity 3 as the **baseline**, open `http://localhost:5150/fetchproducts` in a fresh browser session. In DevTools → Network, filter to `productlist` and enable *Preserve log*. Record number of GET requests.
2. Navigate to Home and back to Products within 15 seconds and record the **additional** GET requests. Repeat 5 times for robustness.
3. Stop Activity 3 and run the final Activity 4 on the same ports. Repeat in an equally fresh browser session. Disable DevTools **Disable cache** for fair client/network behavior; the service cache works independently of browser HTTP caching.
4. With Activity 4, try the explicit **Refresh products** button: it should cause one new GET. This does **not** bypass the back-end 30-second output cache.
5. After 15 seconds, navigate away and back; expect another GET unless a previous action refreshed the client-side lifetime.
6. On the API side, compare `X-InventoryHub-Generation` returned for consecutive requests. Identical values are evidence of output cache reuse; a changed value after expiry shows the endpoint executed again.

| Metric | Baseline observed | Activity 4 observed | Notes |
|---|---|---|---|
| Initial page GET count | _fill in_ | _fill in_ | Usually 1 each |
| Extra GETs on one return navigation (under 15s) | _fill in_ | _fill in_ | Expect 1 vs 0 |
| GETs after manual Refresh | _N/A_ | _fill in_ | Expect 1 |
| CORS or parsing errors | _fill in_ | _fill in_ | Expect none |
| Cached server generation (two rapid GETs) | _N/A_ | _fill in_ | Expect same value |

## B. Measure API HTTP latency with the same benchmark

This benchmark uses Python urllib; it does **not** test client-side Blazor caching. Execute on the same machine, with both server versions started **one at a time** on port 5199. Let startup complete before running the benchmark.

```bash
# Start the ACTIVITY 3 ServerApp (baseline) in a separate terminal:
# dotnet run --project ServerApp --launch-profile http
# Run this from the FINAL project directory:
python scripts/benchmark_api.py --label baseline --samples 50 --output performance/baseline.json

# Stop the Activity 3 server, start the FINAL ServerApp on the same port.
python scripts/benchmark_api.py --label final --samples 50 --output performance/final.json
python scripts/compare_benchmarks.py performance/baseline.json performance/final.json
```

The tool performs one separate warm-up request, then 50 sequential HTTP GETs, reads the response, captures client-observed mean/median/p95 latency and counts distinct `X-InventoryHub-Generation` values in the final server response. The Activity 3 server doesn't expose the generation header, so baseline generation count is `null`. Results are stored as machine-readable JSON; **do not fill in numbers until these commands run**. This small API may have negligible per-request latency; savings in endpoint executions still matter at greater scale.

**Interpretation:** Reduction percentage is `(baseline - final) / baseline × 100`. Positive is improvement, negative is regression. The measurements are local loopback observations including network and scheduling noise—not proof of production CPU or large-scale throughput improvements. For trustworthy comparisons, run several rounds on the same machine, monitor GC/CPU, and use more representative payloads and multiple clients.

## C. Regression checklist

- [ ] `dotnet restore` and `dotnet build` succeed for `FullStackSolution.sln`.
- [ ] API returns 200 JSON with nested category and valid schema.
- [ ] Client displays both products with price, stock and category.
- [ ] No CORS issues in Network/Console; preflight succeeds in Postman.
- [ ] Two sequential API GETs have the same cache-generation header within TTL.
- [ ] Navigating away/back within 15s makes no new client GET.
- [ ] Refresh makes a new GET; after 15s, navigation can refetch.
- [ ] Malformed JSON, server unavailable and timeouts display appropriate errors.
- [ ] After an error, retry works once the API is healthy.
- [ ] Recorded baseline and final measurements are actual local readings.

## Caching trade-offs

- Server's **30-second OutputCache** caches the JSON output of the read-only endpoint. In multi-instance hosting, each server process has its own cache by default.
- Client's **15-second in-memory cache** may combine with server cache staleness. Worst-case visible data age can approach 45 seconds, depending on fetch timing. Inventory write operations need explicit cache invalidation (client + server) or more conservative TTLs.
- The shared fetch's **10-second timeout** is independent from per-component cancellation; navigating away cancels only that component's wait, not another active consumer's request.
- The `X-InventoryHub-Generation` diagnostic header is for exercise verification; consider removing it in production. It does not expose stock data but is an extra implementation detail.
