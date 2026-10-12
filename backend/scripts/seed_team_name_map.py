"""
Maintenance helper for football_data_co_uk_team_map.json.

Prints a report only - it never writes the map file. Run this after
syncing new teams (scripts/sync_all_teams.py) to see which
football-data.co.uk short names can now be mapped to a real, verified
full name that didn't exist in teams.json before, and which short
names still have no match anywhere on this platform.

The candidate suggestions are a normalization heuristic (strip
accents/punctuation/common club-name tokens, then look for a
containment match) meant only to speed up a human's review - never
trust a suggestion without checking it. A wrong pairing here silently
mislabels a real club's historical results as some other club's, so
every suggestion in the output must be verified before being added to
the map file by hand.
"""

import json
import re
import unicodedata
from pathlib import Path

from app.collectors.football_data_co_uk_normalizer import COMPETITION_CODE_MAP
from app.providers.football_data_co_uk_provider import FootballDataCoUkProvider
from app.repositories.team_repository import TeamRepository

TEAM_MAP_PATH = Path(__file__).parent.parent / "app" / "data" / "football_data_co_uk_team_map.json"

# A representative recent season is enough to see the current roster
# per competition - this is about finding NEW candidates, not
# rebuilding the whole historical short-name list.
SAMPLE_SEASON = "2425"

_NOISE_TOKENS = {
    "fc", "afc", "cf", "sc", "ac", "cd", "cs", "sv", "vfb", "rc", "rcd",
    "ud", "sd", "calcio", "clube", "futebol", "de", "club", "the",
}


def _normalize(name: str) -> str:
    stripped = unicodedata.normalize("NFKD", name)
    stripped = "".join(c for c in stripped if not unicodedata.combining(c))
    stripped = re.sub(r"[^a-z0-9 ]", " ", stripped.lower())
    tokens = [t for t in stripped.split() if t not in _NOISE_TOKENS and not t.isdigit()]
    return " ".join(tokens)


def _candidates(short_name: str, full_names: list[str]) -> list[str]:
    normalized_short = _normalize(short_name)

    if not normalized_short:
        return []

    matches = []

    for full_name in full_names:
        normalized_full = _normalize(full_name)

        if normalized_short in normalized_full or normalized_full in normalized_short:
            matches.append(full_name)

    return matches


def main():
    team_map = json.loads(TEAM_MAP_PATH.read_text(encoding="utf-8"))
    team_map.pop("_comment", None)

    full_names = sorted({team["name"] for team in TeamRepository().get_all()})

    provider = FootballDataCoUkProvider()

    try:
        for code, competition in COMPETITION_CODE_MAP.items():
            existing = team_map.get(code, {})

            csv_text = provider.fetch_season_csv(code, SAMPLE_SEASON)
            lines = [line for line in csv_text.splitlines() if line.strip()]

            if not lines:
                continue

            header = lines[0].split(",")
            home_index = header.index("HomeTeam")

            short_names = sorted({
                line.split(",")[home_index]
                for line in lines[1:]
                if line.split(",")[home_index]
            })

            new_short_names = [s for s in short_names if s not in existing]

            if not new_short_names:
                continue

            print(f"\n{code} ({competition}) - {len(new_short_names)} unmapped short name(s):")

            for short_name in new_short_names:
                candidates = _candidates(short_name, full_names)

                if candidates:
                    print(f"   {short_name!r} -> possible match(es): {candidates}")
                else:
                    print(f"   {short_name!r} -> no candidate found (team likely never synced)")
    finally:
        provider.close()

    print(
        "\nVerify each suggestion above before editing "
        "app/data/football_data_co_uk_team_map.json by hand - this "
        "script never writes to it."
    )


if __name__ == "__main__":
    main()
