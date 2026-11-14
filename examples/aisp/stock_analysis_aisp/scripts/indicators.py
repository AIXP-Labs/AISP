#!/usr/bin/env python3
"""indicators.py — compute summary indicators for the stock_analysis_aisp skill.

This is an `execute_only` script resource declared in aisp_contract.resources with
requires_tools: ["shell"]. It is invoked by the `compute` node via `sys.run`, not
injected in full into the model context (mode gating, SE3). It reads a price series
(UTF-8 CSV, optional BOM) on stdin and writes strict JSON on stdout. A unique
close column and finite values are required. Invalid/empty input returns an
error object and exit 1. Volatility is population standard deviation of sampled
closing prices, rounded after calculation, not annualized return volatility.
Zero third-party deps.

Security boundary:
  - Reads stdin only; writes stdout only. No file writes, no network, no subprocess.
  - The host grants only the `shell` tool (least authority, SE4).
"""
import csv
import io
import json
import math
import statistics
import sys


def compute(rows):
    closes = []
    for row in rows:
        if not isinstance(row, dict) or None in row or row.get("close") is None:
            raise ValueError("Each CSV row must contain a close value and match the header")
        close = float(row["close"])
        if not math.isfinite(close):
            raise ValueError("Close prices must be finite numbers")
        closes.append(close)
    if not closes:
        raise ValueError("No close prices found")
    n = len(closes)
    moving_average = round(statistics.mean(closes), 4)
    volatility = round(statistics.pstdev(closes), 4)
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
    try:
        text = sys.stdin.buffer.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        if not reader.fieldnames or reader.fieldnames.count("close") != 1:
            raise ValueError("CSV must contain exactly one close column")
        result = compute(reader)
        code = 0
    except (ValueError, TypeError, ArithmeticError, csv.Error) as exc:
        result = {"error": str(exc)}
        code = 1
    json.dump(result, sys.stdout, allow_nan=False)
    sys.stdout.write("\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
