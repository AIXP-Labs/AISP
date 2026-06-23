#!/usr/bin/env python3
"""indicators.py — compute summary indicators for the stock_analysis_aisp skill.

This is an `execute_only` script resource declared in aisp_contract.resources with
requires_tools: ["shell"]. It is invoked by the `compute` node via `sys.run`, not
injected in full into the model context (mode gating, SE3). It reads a price series
(CSV text) on stdin and writes a JSON summary on stdout. Zero third-party deps.

Security boundary:
  - Reads stdin only; writes stdout only. No file writes, no network, no subprocess.
  - The host grants only the `shell` tool (least authority, SE4).
"""
import csv
import io
import json
import sys


def compute(rows):
    closes = [float(r["close"]) for r in rows if r.get("close")]
    if not closes:
        return {"error": "no close prices found"}
    n = len(closes)
    moving_average = round(sum(closes) / n, 4)
    mean = moving_average
    variance = sum((c - mean) ** 2 for c in closes) / n
    volatility = round(variance ** 0.5, 4)
    trend = "up" if closes[-1] > closes[0] else "down" if closes[-1] < closes[0] else "flat"
    return {
        "moving_average": moving_average,
        "volatility": volatility,
        "trend": trend,
        "first_close": closes[0],
        "last_close": closes[-1],
        "samples": n,
    }


def main():
    text = sys.stdin.read()
    rows = list(csv.DictReader(io.StringIO(text)))
    json.dump(compute(rows), sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
