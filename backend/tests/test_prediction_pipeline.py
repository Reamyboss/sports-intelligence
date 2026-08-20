import pytest

from app.evidence.evidence_builder import build_evidence
from app.evidence.goal_evidence import get_goal_statistics
from app.knowledge.knowledge_builder import build_match_profile
from app.prediction.prediction_service import run_prediction
from app.services.match_service import MatchService


def test_full_pipeline_produces_a_structurally_valid_prediction(real_match_id):
    """
    Runs every layer - knowledge, evidence, reasoning, confidence,
    prediction - against a real match from app/data/matches.json.

    Asserts structure/invariants rather than exact values, since the
    underlying data is live-synced and will change over time.
    """

    match = MatchService().get_match(real_match_id)

    profile = build_match_profile(match)
    evidence = build_evidence(profile, match_id=match.id, kickoff=match.kickoff)
    result = run_prediction(evidence=evidence, supporting_evidence=[])

    by_outcome = {
        "HOME": result.home_probability,
        "DRAW": result.draw_probability,
        "AWAY": result.away_probability,
    }

    assert result.winner in ("HOME", "AWAY", "DRAW")

    # The reported probability is the predicted outcome's own share,
    # and it is the largest of the three - not a home-lean index that
    # happens to sit in a fixed band.
    assert result.probability == by_outcome[result.winner]
    assert result.probability == max(by_outcome.values())
    assert sum(by_outcome.values()) == pytest.approx(100.0, abs=0.05)

    assert 0.0 <= result.confidence <= 100.0
    assert result.market == "MATCH_WINNER"
    assert isinstance(result.explanation, list)
    assert result.reasoning.summary
    assert result.summary
    assert match.home_team in result.summary or match.away_team in result.summary


def test_pipeline_evidence_has_expected_shape_for_both_teams(real_match_id):
    match = MatchService().get_match(real_match_id)

    profile = build_match_profile(match)
    evidence = build_evidence(profile, match_id=match.id, kickoff=match.kickoff)

    for side in ("home_team", "away_team"):
        assert set(evidence[side]["goals"]) == {
            "matches",
            "goals_scored",
            "goals_conceded",
            "avg_goals_scored",
            "avg_goals_conceded",
        }
        assert isinstance(evidence[side]["form"], list)

    assert set(evidence["head_to_head"]) == {
        "matches",
        "home_wins",
        "draws",
        "away_wins",
    }


def test_established_team_actually_has_finished_match_history():
    """
    Regression guard: get_finished_matches_by_team() used to only
    check matches.json (which can never contain a finished match),
    so this evidence silently came back empty for every team,
    including ones with a full season of real results on file.

    Arsenal FC is used because it's about as safe a bet as exists for
    "a team with a real, permanent Premier League match history".
    """

    stats = get_goal_statistics("Arsenal FC")

    assert stats["matches"] > 0
