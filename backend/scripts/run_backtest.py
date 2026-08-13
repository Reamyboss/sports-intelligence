"""
Runs the historical backtest and prints the full comparison report.

python scripts/run_backtest.py
"""

import functools
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.backtesting.dataset import load_backtest_matches
from app.backtesting.metrics import compute_metrics, format_report
from app.backtesting.runner import run_backtest
from app.repositories.match_repository import MatchRepository


def _enable_read_caching() -> None:
    """
    Every evidence/knowledge module owns its own MatchRepository()
    instance, and get_all_matches()/get_all_historical_matches()
    re-read and re-parse the full JSON file from disk on every call -
    fine for one live request, far too slow when the same two static
    files get read ~12 times per backtested match across thousands of
    matches. This patches the class in-process, for this script's
    process only - app/repositories/match_repository.py itself is
    never modified, and this never runs during pytest (separate
    process), so the test suite is unaffected.
    """

    @functools.lru_cache(maxsize=8)
    def _load(path_str: str) -> list:
        with open(path_str, encoding="utf-8") as file:
            return json.load(file)

    def cached_get_all_matches(self):
        if not self.matches_file.exists():
            return []
        return _load(str(self.matches_file))

    def cached_get_all_historical_matches(self):
        if not self.historical_matches_file.exists():
            return []
        return _load(str(self.historical_matches_file))

    MatchRepository.get_all_matches = cached_get_all_matches
    MatchRepository.get_all_historical_matches = cached_get_all_historical_matches


def main() -> None:
    _enable_read_caching()

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
