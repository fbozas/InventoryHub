"""Report observed baseline/optimized differences without inventing metrics.

python scripts/compare_benchmarks.py baseline.json optimized.json
"""
import argparse
import json
from pathlib import Path


def reduction_percentage(before, after):
    if before <= 0:
        raise ValueError("Baseline must be greater than zero")
    return (before - after) / before * 100


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("optimized", type=Path)
    args = parser.parse_args()
    before = json.loads(args.baseline.read_text(encoding="utf-8"))
    after = json.loads(args.optimized.read_text(encoding="utf-8"))
    if before["samples"] != after["samples"]:
        raise SystemExit("Use the same --samples for both benchmarks")
    if before["url"] != after["url"]:
        raise SystemExit("Use the same URL for both benchmarks")
    print("Client-observed HTTP latency; negative reductions indicate regressions.")
    for name in ("median_ms", "mean_ms", "p95_ms"):
        reduction = reduction_percentage(before[name], after[name])
        print(f"{name}: baseline {before[name]:.3f}ms, final {after[name]:.3f}ms, "
              f"change {reduction:+.1f}%")
    print("Caution: network jitter and tiny mock endpoints may mask any improvement.")


if __name__ == "__main__":
    main()
