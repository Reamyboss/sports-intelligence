from app.confidence.confidence_engine import calculate_confidence
from app.knowledge.match_profile import MatchProfile
from app.reasoning.explanation_engine import explain


def predict(profile: MatchProfile) -> dict:
    score = 0

    if profile.home_advantage:
        score += 1

    score += profile.home_form.count("W")
    score -= profile.away_form.count("W")

    if score > 0:
        probability = 65.0
        winner = profile.home_team
    else:
        probability = 55.0
        winner = profile.away_team

    return {
        "winner": winner,
        "probability": probability,
        "confidence": calculate_confidence(probability),
        "reasons": explain(profile),
    }