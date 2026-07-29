from app.repositories.match_repository import MatchRepository

repo = MatchRepository()

matches = repo.get_finished_matches_by_team("Arsenal FC")

print(f"Found {len(matches)} finished matches")

for match in matches[:5]:
    print(match["home_team"], "vs", match["away_team"], "-", match["status"])