import json
from pathlib import Path

from app.collectors.football_data_co_uk_collector import FootballDataCoUkCollector

# Short-horizon evidence (form/streak/rest) gets essentially no value
# from seasons more than a year or two old - this window exists to
# give a future ML model enough training rows without reaching into
# tactically-irrelevant eras. Adjust here, not by restructuring code.
SEASONS = [
    "1516", "1617", "1718", "1819", "1920",
    "2021", "2122", "2223", "2324", "2425",
]

CODES = ["E0", "E1", "SP1", "D1", "I1", "F1", "N1", "P1"]

TEAM_MAP_PATH = Path(__file__).parent.parent / "app" / "data" / "football_data_co_uk_team_map.json"


def _season_start_year(season: str) -> int:
    return 2000 + int(season[:2])


def main():
    team_map = json.loads(TEAM_MAP_PATH.read_text(encoding="utf-8"))
    team_map.pop("_comment", None)

    collector = FootballDataCoUkCollector(team_map)

    all_unmatched: set[str] = set()

    try:
        for code in CODES:
            for season in SEASONS:
                result = collector.collect(code, season, _season_start_year(season))

                print(
                    f"{code} {season}: fetched={result.fetched} saved={result.saved} "
                    f"duplicate={result.skipped_duplicate} "
                    f"unmapped_home={result.skipped_unmapped_home} "
                    f"unmapped_away={result.skipped_unmapped_away} "
                    f"missing_field={result.skipped_missing_field} "
                    f"unparseable={result.skipped_unparseable}",
                    flush=True,
                )

                all_unmatched |= result.unmatched_teams
    finally:
        collector.close()

    if all_unmatched:
        print(
            "\nUnmatched short names (never synced under this platform - "
            "no verified full name exists yet; re-run "
            "scripts/seed_team_name_map.py after syncing more teams to "
            "see what can now be added to football_data_co_uk_team_map.json):"
        )
        for name in sorted(all_unmatched):
            print("   ", name)


if __name__ == "__main__":
    main()
