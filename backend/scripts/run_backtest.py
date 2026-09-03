"""
Runs the historical backtest and prints the full comparison report.

python scripts/run_backtest.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.backtesting.dataset import load_backtest_matches
from app.backtesting.metrics import compute_metrics, format_report
from app.backtesting.runner import run_backtest


def main() -> None:
    print("Loading historical matches...", flush=True)
    matches = load_backtest_matches()
    print(f"{len(matches)} finished historical matches loaded.", flush=True)

    start = time.time()
    results = run_backtest(matches)
    elapsed = time.time() - start
    print(f"Backtest completed in {elapsed:.1f}s ({elapsed / len(results) * 1000:.1f}ms/match).", flush=True)

    metrics = compute_metrics(results)
    print(format_report(metrics))


if __name__ == "__main__":
    main()
