from app.evidence.evidence_models import Evidence
from app.reasoning.reasoning_models import ReasoningResult

# The constants the original probability formula was built from. The
# draw band matches predict_match_winner()'s +/-1 threshold exactly,
# so the probabilities and the verdict can never disagree.
BASELINE = 50.0
SLOPE = 8.0
DRAW_BAND = 1.0

# Floor for a single outcome's lean before normalisation, so an
# extreme score can drive an outcome towards zero without ever
# producing a negative share.
MIN_LEAN = 2.0


def _evidence_score(supporting_evidence: list[Evidence]) -> float:
    """
    Turn structured Evidence into a signed score.

    Evidence.strength is on a different scale per signal (a goals
    differential and a head-to-head win differential aren't the same
    unit), so raw strengths can't be summed directly without one
    large-scale signal silently dominating. Each item's strength is
    instead saturated into (0, 1) via strength / (strength + 1) -
    small differentials contribute weakly, large ones approach but
    never reach full weight - then signed by which side it supports.

    Returns 0.0 when there is no supporting evidence, so this is a
    pure extension: predictions built from count-only reasoning
    (the case for every match with no real evidence, and for every
    existing test that doesn't set supporting_evidence) are completely
    unaffected.
    """

    total = 0.0

    for item in supporting_evidence:
        magnitude = item.strength / (item.strength + 1.0)
        total += magnitude if item.supports == "HOME" else -magnitude

    return total


def reasoning_score(reasoning: ReasoningResult) -> float:
    """
    The engine's signed lean: positive favours HOME, negative favours
    AWAY, near zero means neither.

    Extracted verbatim from predict_match_winner() so the probability
    distribution can be derived from the same number the winner is
    decided by, instead of being recomputed differently somewhere else.
    """

    score = 0

    score += len(reasoning.strengths)

    score += len(reasoning.opportunities)

    score -= len(reasoning.weaknesses)

    score -= len(reasoning.risks)

    score -= len(reasoning.contradictions)

    score += _evidence_score(reasoning.supporting_evidence)

    return score


def match_probabilities(reasoning: ReasoningResult) -> tuple[float, float, float]:
    """
    Convert the engine's lean into (home, draw, away) probabilities
    that sum to 100.

    This is a re-representation, not a new model. It reuses the
    existing constants - the 50 baseline, the 8-points-per-unit slope,
    and the +/-1 draw band that predict_match_winner() already decides
    with - and simply reads them symmetrically:

        home lean  = 50 + 8 * score      (the original formula)
        away lean  = 50 - 8 * score      (the same formula, mirrored)
        draw lean  = 58, decaying by 8 per unit outside the draw band

    The draw is flat inside the band and falls away outside it, which
    makes the distribution's largest value always the side
    predict_match_winner() picks - so the number shown beside a team
    is that team's probability, and it can never contradict the
    verdict printed next to it.

    The old code exposed `50 + score * 8` clamped to [40, 90] as
    "probability" for every outcome, so an away pick always surfaced
    as 40-42% - the chance of the *home* team, presented as the chance
    of the away team.
    """

    score = reasoning_score(reasoning)
    lean = abs(score)

    home_lean = BASELINE + (SLOPE * score)
    away_lean = BASELINE - (SLOPE * score)
    draw_lean = BASELINE + (SLOPE * DRAW_BAND) - (SLOPE * max(0.0, lean - DRAW_BAND))

    leans = [max(MIN_LEAN, value) for value in (home_lean, draw_lean, away_lean)]
    total = sum(leans)

    home, draw, away = (value / total * 100 for value in leans)

    return round(home, 2), round(draw, 2), round(away, 2)


def probability_of(winner: str, probabilities: tuple[float, float, float]) -> float:
    """Pick out the probability belonging to the predicted outcome."""

    home, draw, away = probabilities

    if winner == "HOME":
        return home

    if winner == "AWAY":
        return away

    return draw


def predict_match_winner(
    reasoning: ReasoningResult,
) -> tuple[str, float]:
    """
    Determine the predicted winner using reasoning.

    The second element is the raw home-lean index, kept unchanged so
    the decision boundaries and every existing test around them still
    hold. It is an internal quantity - what reaches the API is
    match_probabilities().
    """

    score = reasoning_score(reasoning)

    if score > 1:
        prediction = "HOME"

    elif score < -1:
        prediction = "AWAY"

    else:
        prediction = "DRAW"

    probability = max(
        40.0,
        min(
            90.0,
            50 + (score * 8),
        ),
    )

    return prediction, probability