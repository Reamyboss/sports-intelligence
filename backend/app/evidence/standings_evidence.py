from datetime import datetime

from app.repositories.match_repository import MatchRepository
from app.utils.helpers import parse_kickoff

repository = MatchRepository()

WIN_POINTS = 3
DRAW_POINTS = 1

# Competitions where a single combined table is not a real thing.
# These run separate groups and then a knockout bracket, so ranking
# every entrant against every other by points would present a
# standing that does not exist in the competition itself. The
# Champions League is deliberately NOT here: since 2024/25 its league
# phase is one 36-team table, so a position in it is real.
NON_LEAGUE_COMPETITIONS = {
    "FIFA World Cup",
    "European Championship",
}


def _table(competition: str, season, before: datetime | None, exclude_match_id: int | None) -> dict:
    """
    The league table as it stood immediately before `before`, built
    only from finished matches in the same competition and season.

    Sourced from matches.json alone, deliberately. The two data files
    do not share a competition vocabulary - matches.json says
    "Premier League" where historical_matches.json says "PL" - so
    joining them by competition name would silently produce a table
    missing every row from the other file. Every match the prediction
    API can serve comes from matches.json, so a table built from it is
    complete for that match and internally consistent.
    """

    standings: dict[str, dict] = {}

    for match in repository.get_all_matches():
        if match.get("competition") != competition or match.get("season") != season:
            continue

        if str(match.get("status", "")).lower() != "finished":
            continue

        if exclude_match_id is not None and match.get("id") == exclude_match_id:
            continue

        kickoff = parse_kickoff(match)

        if kickoff is None:
            continue

        if before is not None and kickoff >= before:
            continue

        home_score = match.get("home_score")
        away_score = match.get("away_score")

        if home_score is None or away_score is None:
            continue

        for side, scored, conceded in (
            (match["home_team"], home_score, away_score),
            (match["away_team"], away_score, home_score),
        ):
            row = standings.setdefault(
                side,
                {"team": side, "played": 0, "points": 0, "goals_for": 0, "goals_against": 0},
            )

            row["played"] += 1
            row["goals_for"] += scored
            row["goals_against"] += conceded

            if scored > conceded:
                row["points"] += WIN_POINTS
            elif scored == conceded:
                row["points"] += DRAW_POINTS

    return standings


def get_standings_snapshot(
    team: str,
    competition: str,
    season,
    before: datetime | None = None,
    exclude_match_id: int | None = None,
) -> dict | None:
    """
    Where `team` sat in its competition immediately before this match.

    Returns None - never a fabricated position - when the standing
    genuinely does not exist: a competition that has no single table
    (see NON_LEAGUE_COMPETITIONS), a season with no completed matches
    yet, or a team with no completed matches of its own. An
    unplaced team at the start of a season has no position, and
    reporting one would be an invention.

    Ordering is the standard one: points, then goal difference, then
    goals scored, with team name last purely so the result is stable
    rather than arbitrary when sides are genuinely level.
    """

    if competition in NON_LEAGUE_COMPETITIONS:
        return None

    standings = _table(competition, season, before, exclude_match_id)

    if not standings or team not in standings:
        return None

    ordered = sorted(
        standings.values(),
        key=lambda row: (
            -row["points"],
            -(row["goals_for"] - row["goals_against"]),
            -row["goals_for"],
            row["team"],
        ),
    )

    for position, row in enumerate(ordered, start=1):
        if row["team"] == team:
            return {
                "position": position,
                "teams_in_table": len(ordered),
                "played": row["played"],
                "points": row["points"],
                "goals_for": row["goals_for"],
                "goals_against": row["goals_against"],
                "goal_difference": row["goals_for"] - row["goals_against"],
            }

    return None
