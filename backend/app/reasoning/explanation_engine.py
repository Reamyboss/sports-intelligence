from app.knowledge.match_profile import MatchProfile


def explain(profile: MatchProfile) -> list[str]:
    reasons = []

    if profile.home_advantage:
        reasons.append("Home advantage")

    if profile.home_form.count("W") > profile.away_form.count("W"):
        reasons.append("Better recent form")

    if (
        profile.head_to_head["home_wins"]
        > profile.head_to_head["away_wins"]
    ):
        reasons.append("Superior head-to-head record")

    return reasons