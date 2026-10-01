from app.evidence.evidence_models import Evidence
from app.prediction.prediction_models import PredictionResult
from app.reasoning.reasoning_models import ReasoningResult
from app.social.x_posts import (
    X_LIMIT,
    pick_post,
    receipt_post,
    short_name,
    x_length,
)

HOME, AWAY = "Arsenal FC", "AFC Bournemouth"


def _prediction(winner="HOME", support=(), opposition=None) -> PredictionResult:
    reasoning = ReasoningResult(
        home_team=HOME,
        away_team=AWAY,
        strengths=[], weaknesses=[], risks=[], opportunities=[],
        contradictions=[], summary="",
        supporting_evidence=list(support) + ([opposition] if opposition else []),
    )
    return PredictionResult(
        winner=winner,
        probability=61.0,
        home_probability=61.0,
        draw_probability=24.0,
        away_probability=15.0,
        confidence=70.0,
        strongest_opposition=opposition,
        market="MATCH_WINNER",
        reasoning=reasoning,
        explanation=[],
        summary="",
    )


def _ev(supports, strength, reason="x" * 60):
    return Evidence(title="T", supports=supports, strength=strength, reason=reason)


def test_short_name_strips_club_suffixes():
    assert short_name("Arsenal FC") == "Arsenal"
    assert short_name("AFC Bournemouth") == "Bournemouth"
    assert short_name("Hull City AFC") == "Hull City"


def test_pick_post_always_fits_even_with_long_evidence():
    support = [_ev("HOME", s, "Arsenal FC " + "y" * 150) for s in (3, 2, 1)]
    post = pick_post(_prediction(support=support, opposition=_ev("AWAY", 5, "z" * 200)),
                     HOME, AWAY, "Premier League", "Sat 10 Oct")
    assert x_length(post) <= X_LIMIT
    assert "Arsenal win (61%)" in post


def test_pick_post_without_evidence_says_it_is_a_lean():
    post = pick_post(_prediction(), HOME, AWAY, "Premier League", "Sat")
    assert "lean, not a lock" in post


def test_weak_opposition_is_not_presented_as_the_risk():
    post = pick_post(_prediction(opposition=_ev("AWAY", 1.0, "one more rest day")),
                     HOME, AWAY, "Premier League", "Sat")
    assert "one more rest day" not in post
    assert "nothing in my data" in post


def test_receipt_grades_hits_and_misses():
    pred = _prediction(opposition=_ev("AWAY", 3, "Bournemouth are unbeaten away"))
    assert receipt_post(pred, HOME, AWAY, 2, 0).startswith("✅")
    miss = receipt_post(pred, HOME, AWAY, 1, 1)
    assert miss.startswith("❌")
    assert "Bournemouth are unbeaten away" in miss
    assert x_length(miss) <= X_LIMIT
