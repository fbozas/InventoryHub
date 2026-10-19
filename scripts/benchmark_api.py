"""Measure live API HTTP response time and save reproducible measurements.

Use this exact script for Activity 3 (baseline) AND Activity 4 (optimized),
with the same machine, server mode, request count, and URL.

python scripts/benchmark_api.py --label baseline --output baseline.json
python scripts/benchmark_api.py --label optimized --output optimized.json

This measures *client-observed* HTTP latency, not server CPU. For client-side
request count, use your browser's DevTools Network tab (see PERFORMANCE.md).
"""

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


def percentile(samples, percentile_value):
    """Linear-interpolated percentile over a sorted, nonempty sample."""
    if not samples:
        raise ValueError("Cannot calculate a percentile without samples")
    ordered = sorted(samples)
    index = (len(ordered) - 1) * percentile_value / 100
    left = int(index)
    right = min(left + 1, len(ordered) - 1)
    return ordered[left] + (ordered[right] - ordered[left]) * (index - left)


def measure(url, samples, timeout):
    timings = []
    generations = []
    for _ in range(samples):
        # urllib does not maintain a browser HTTP response cache.
        request = Request(url, headers={"Accept": "application/json"})
        start = time.perf_counter()
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            if response.status != 200:
                raise RuntimeError(f"Unexpected HTTP status: {response.status}")
            if "application/json" not in response.headers.get("Content-Type", ""):
                raise RuntimeError("Unexpected Content-Type")
            generation = response.headers.get("X-InventoryHub-Generation")
        timings.append(round((time.perf_counter() - start) * 1000, 4))
        generations.append(generation)
        if not body:
            raise RuntimeError("Empty API response")
    return timings, generations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:5199/api/productlist")
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--timeout", type=float, default=5)
    args = parser.parse_args()
    if args.samples < 2:
        parser.error("--samples must be >= 2 (warm-up + measured samples)")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    # A warm-up request allows JIT/endpoint initialization before measurements.
    measure(args.url, 1, args.timeout)
    timings, generations = measure(args.url, args.samples, args.timeout)
    result = {
        "label": args.label,
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "url": args.url,
        "samples": args.samples,
        "mean_ms": round(statistics.mean(timings), 4),
        "median_ms": round(statistics.median(timings), 4),
        "p95_ms": round(percentile(timings, 95), 4),
        "min_ms": min(timings),
        "max_ms": max(timings),
        "unique_generation_count": len(set(g for g in generations if g is not None))
            if any(g is not None for g in generations) else None,
        "generation_header_present": all(g is not None for g in generations),
        "timings_ms": timings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{args.label}: n={args.samples}, median={result['median_ms']:.3f}ms, "
          f"p95={result['p95_ms']:.3f}ms, mean={result['mean_ms']:.3f}ms")
    print(f"Unique endpoint generations: {result['unique_generation_count']}; "
          f"results saved to {args.output}")


if __name__ == "__main__":
    main()
