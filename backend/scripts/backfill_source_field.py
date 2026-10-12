"""
One-time migration: stamps every existing historical_matches.json
record with source="football-data.org" before the
football-data.co.uk collector ever runs.

Without this, "source is absent" would be an ambiguous state once
two sources coexist in the same file - every record must say where
it came from, not leave it to be inferred.

Safe to re-run: records that already have a source are left alone.
"""

from app.repositories.match_repository import MatchRepository


def main():
    repository = MatchRepository()
    matches = repository.get_all_historical_matches()

    stamped = 0

    for match in matches:
        if "source" not in match:
            match["source"] = "football-data.org"
            stamped += 1

    if stamped:
        repository.save_historical_matches(matches)

    print(f"Stamped {stamped} of {len(matches)} historical matches with source=football-data.org.")


if __name__ == "__main__":
    main()
