from app.reasoning.reasoning_models import ReasoningResult


def evaluate_strengths(evidence: dict) -> list[str]:
    strengths = []

    if evidence["home_team"]["form"].count("W") > evidence["away_team"]["form"].count("W"):
        strengths.append("Home team has stronger recent form.")

    if (
        evidence["home_team"]["goals"]["avg_goals_scored"]
        > evidence["away_team"]["goals"]["avg_goals_scored"]
    ):
        strengths.append("Home team scores more goals on average.")

    return strengths


def evaluate_weaknesses(evidence: dict) -> list[str]:
    weaknesses = []

    if (
        evidence["home_team"]["goals"]["avg_goals_conceded"]
        > evidence["away_team"]["goals"]["avg_goals_conceded"]
    ):
        weaknesses.append("Home team concedes more goals.")

    return weaknesses


def evaluate_risks(evidence: dict) -> list[str]:
    risks = []

    if evidence["away_team"]["form"].count("W") >= 3:
        risks.append("Away team arrives in strong form.")

    return risks


def evaluate_opportunities(evidence: dict) -> list[str]:
    opportunities = []

    if evidence["head_to_head"]["home_wins"] > evidence["head_to_head"]["away_wins"]:
        opportunities.append("Historical head-to-head favors the home team.")

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

    return contradictions