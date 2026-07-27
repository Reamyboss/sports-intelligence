from app.knowledge.match_profile import MatchProfile


def collect_evidence(profile: MatchProfile) -> list[dict]:
    evidence = []

    evidence.append(
        {
            "factor": "Home Advantage",
            "value": profile.home_advantage,
            "weight": 8,
        }
    )

    evidence.append(
        {
            "factor": "Recent Form",
            "value": f"{''.join(profile.home_form)} vs {''.join(profile.away_form)}",
            "weight": 12,
        }
    )

    evidence.append(
        {
            "factor": "Head To Head",
            "value": profile.head_to_head,
            "weight": 6,
        }
    )

    evidence.append(
        {
            "factor": "Rest Days",
            "value": f"{profile.rest_days_home} vs {profile.rest_days_away}",
            "weight": 2,
        }
    )

    return evidence
