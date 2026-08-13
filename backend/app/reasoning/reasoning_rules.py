# Minimum sample sizes before a home/away split or a streak is
# treated as real signal rather than noise from a handful of games.
MIN_HOME_AWAY_SAMPLE = 3
STRONG_WIN_RATE = 0.6
STRONG_AWAY_WIN_RATE = 0.5
STRONG_WINNING_STREAK = 3
NOTABLE_LOSING_STREAK = 2


def _win_rate(side: dict | None) -> float | None:
    if not side:
        return None

    played = sum(side.values())

    if played < MIN_HOME_AWAY_SAMPLE:
        return None

    return side["wins"] / played


def evaluate_strengths(evidence: dict) -> list[str]:
    strengths = []

    if evidence["home_team"]["form"].count("W") > evidence["away_team"]["form"].count("W"):
        strengths.append("Home team has stronger recent form.")

    if (
        evidence["home_team"]["goals"]["avg_goals_scored"]
        > evidence["away_team"]["goals"]["avg_goals_scored"]
    ):
        strengths.append("Home team scores more goals on average.")

    home_win_rate = _win_rate(evidence["home_team"].get("home_away", {}).get("home"))
    if home_win_rate is not None and home_win_rate >= STRONG_WIN_RATE:
        strengths.append("Home team has a strong home-performance record.")

    home_streak = evidence["home_team"].get("streak")
    if home_streak and home_streak.get("winning_streak", 0) >= STRONG_WINNING_STREAK:
        strengths.append("Home team is on a strong winning streak.")

    return strengths


def evaluate_weaknesses(evidence: dict) -> list[str]:
    weaknesses = []

    if (
        evidence["home_team"]["goals"]["avg_goals_conceded"]
        > evidence["away_team"]["goals"]["avg_goals_conceded"]
    ):
        weaknesses.append("Home team concedes more goals.")

    home_streak = evidence["home_team"].get("streak")
    if home_streak and home_streak.get("losing_streak", 0) >= NOTABLE_LOSING_STREAK:
        weaknesses.append("Home team is on a losing streak.")

    return weaknesses


def evaluate_risks(evidence: dict) -> list[str]:
    risks = []

    if evidence["away_team"]["form"].count("W") >= 3:
        risks.append("Away team arrives in strong form.")

    away_win_rate = _win_rate(evidence["away_team"].get("home_away", {}).get("away"))
    if away_win_rate is not None and away_win_rate >= STRONG_AWAY_WIN_RATE:
        risks.append("Away team has a strong away-performance record.")

    away_streak = evidence["away_team"].get("streak")
    if away_streak and away_streak.get("winning_streak", 0) >= STRONG_WINNING_STREAK:
        risks.append("Away team is on a strong winning streak.")

    return risks


def evaluate_opportunities(evidence: dict) -> list[str]:
    opportunities = []

    if evidence["head_to_head"]["home_wins"] > evidence["head_to_head"]["away_wins"]:
        opportunities.append("Historical head-to-head favors the home team.")

    away_streak = evidence["away_team"].get("streak")
    if away_streak and away_streak.get("losing_streak", 0) >= NOTABLE_LOSING_STREAK:
        opportunities.append("Away team is on a losing streak.")

    return opportunities


def evaluate_contradictions(evidence: dict) -> list[str]:
    contradictions = []

    if (
        evidence["home_team"]["form"].count("W") > evidence["away_team"]["form"].count("W")
        and evidence["home_team"]["goals"]["avg_goals_scored"]
        < evidence["away_team"]["goals"]["avg_goals_scored"]
    ):
        contradictions.append(
            "Home team wins more often but scores fewer goals."
        )

    home_streak = evidence["home_team"].get("streak") or {}
    away_streak = evidence["away_team"].get("streak") or {}

    home_has_momentum = home_streak.get("winning_streak", 0) >= 2
    away_has_momentum = away_streak.get("winning_streak", 0) >= 2

    h2h_favors_home = (
        evidence["head_to_head"]["home_wins"] > evidence["head_to_head"]["away_wins"]
    )
    h2h_favors_away = (
        evidence["head_to_head"]["away_wins"] > evidence["head_to_head"]["home_wins"]
    )

    if h2h_favors_home and away_has_momentum and not home_has_momentum:
        contradictions.append(
            "Historical head-to-head favors the home team, but recent form "
            "favors the away team."
        )

    if h2h_favors_away and home_has_momentum and not away_has_momentum:
        contradictions.append(
            "Historical head-to-head favors the away team, but recent form "
            "favors the home team."
        )

    return contradictions
