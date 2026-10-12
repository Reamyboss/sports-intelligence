"""
Reports how many historical matches come from which source, per
competition - so "what's real-time-synced vs. bulk historical" is
always answerable, not something to infer from file size.
"""

from collections import Counter

from app.repositories.match_repository import MatchRepository


def main():
    matches = MatchRepository().get_all_historical_matches()

    by_source = Counter(match.get("source", "football-data.org") for match in matches)
    by_source_and_competition = Counter(
        (match.get("source", "football-data.org"), match.get("competition"))
        for match in matches
    )

    print(f"Total historical matches: {len(matches)}\n")

    print("By source:")
    for source, count in by_source.most_common():
        print(f"   {source}: {count}")

    print("\nBy source and competition:")
    for (source, competition), count in sorted(by_source_and_competition.items()):
        print(f"   {source} / {competition}: {count}")


if __name__ == "__main__":
    main()
