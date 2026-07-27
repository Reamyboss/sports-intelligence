from app.confidence.confidence_engine import calculate_confidence
from app.evidence.evidence_engine import collect_evidence
from app.knowledge.match_profile import MatchProfile
from app.reasoning.explanation_engine import explain


def predict(profile: MatchProfile) -> dict:
    """
    Predict the most likely winner of a match based on the
    current knowledge profile.
    """

    score = 0

    # Home advantage
    if profile.home_advantage:
        score += 1

    # Recent form
    score += profile.home_form.count("W")
    score -= profile.away_form.count("W")

    # Determine winner
    if score > 0:
        winner = profile.home_team
        probability = 65.0
    else:
        winner = profile.away_team
        probability = 55.0

    # Build supporting data
    reasons = explain(profile)
    evidence = collect_evidence(profile)
    confidence = calculate_confidence(probability)

    # Return prediction
    return {
        "winner": winner,
        "probability": probability,
        "confidence": confidence,
        "reasons": reasons,
        "evidence": evidence,
    }
