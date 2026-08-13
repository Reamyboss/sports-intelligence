from datetime import datetime

from app.evidence.evidence_builder import build_evidence, build_supporting_evidence
from app.knowledge.match_profile import MatchProfile


def make_evidence(
    home_form=None,
    away_form=None,
    home_avg_scored=0.0,
    away_avg_scored=0.0,
    home_matches=0,
    away_matches=0,
    h2h_home_wins=0,
    h2h_away_wins=0,
    h2h_draws=0,
    h2h_matches=0,
    home_winning_streak=0,
    home_losing_streak=0,
    away_winning_streak=0,
    away_losing_streak=0,
    home_last_10=None,
    away_last_10=None,
    home_home_wins=0,
    home_home_played=0,
    away_away_wins=0,
    away_away_played=0,
    home_name="Home FC",
    away_name="Away FC",
):
    def home_away_side(wins, played):
        losses = played - wins
        return {"wins": wins, "draws": 0, "losses": losses}

    return {
        "home_team": {
            "name": home_name,
            "form": home_form or [],
            "goals": {
                "matches": home_matches,
                "goals_scored": 0,
                "goals_conceded": 0,
                "avg_goals_scored": home_avg_scored,
                "avg_goals_conceded": 0.0,
            },
            "home_away": {
                "home": home_away_side(home_home_wins, home_home_played),
                "away": {"wins": 0, "draws": 0, "losses": 0},
            },
            "streak": {
                "winning_streak": home_winning_streak,
                "unbeaten_streak": 0,
                "losing_streak": home_losing_streak,
                "winless_streak": 0,
                "last_10_results": home_last_10 or [],
            },
            "rest": {"days_rest": None},
        },
        "away_team": {
            "name": away_name,
            "form": away_form or [],
            "goals": {
                "matches": away_matches,
                "goals_scored": 0,
                "goals_conceded": 0,
                "avg_goals_scored": away_avg_scored,
                "avg_goals_conceded": 0.0,
            },
            "home_away": {
                "home": {"wins": 0, "draws": 0, "losses": 0},
                "away": home_away_side(away_away_wins, away_away_played),
            },
            "streak": {
                "winning_streak": away_winning_streak,
                "unbeaten_streak": 0,
                "losing_streak": away_losing_streak,
                "winless_streak": 0,
                "last_10_results": away_last_10 or [],
            },
            "rest": {"days_rest": None},
        },
        "head_to_head": {
            "matches": h2h_matches,
            "home_wins": h2h_home_wins,
            "draws": h2h_draws,
            "away_wins": h2h_away_wins,
        },
    }


# -----------------------------
# Real signal produces real, grounded Evidence
# -----------------------------


def test_form_difference_produces_evidence_supporting_the_leader():
    evidence = make_evidence(
        home_form=["W", "W", "W", "L", "L"],
        away_form=["L", "L", "L", "W", "W"],
    )

    items = build_supporting_evidence(evidence)
    form_items = [i for i in items if i.title == "Recent Form"]

    assert len(form_items) == 1
    assert form_items[0].supports == "HOME"
    assert form_items[0].strength == 1.0
    assert "Home FC" in form_items[0].reason


def test_goals_difference_produces_evidence():
    evidence = make_evidence(
        home_avg_scored=2.5, away_avg_scored=1.0, home_matches=10, away_matches=10,
    )

    items = build_supporting_evidence(evidence)
    goal_items = [i for i in items if i.title == "Goals Scored"]

    assert len(goal_items) == 1
    assert goal_items[0].supports == "HOME"
    assert goal_items[0].strength == 1.5


def test_head_to_head_difference_produces_evidence():
    evidence = make_evidence(h2h_home_wins=4, h2h_away_wins=1, h2h_draws=1, h2h_matches=6)

    items = build_supporting_evidence(evidence)
    h2h_items = [i for i in items if i.title == "Head-to-Head"]

    assert len(h2h_items) == 1
    assert h2h_items[0].supports == "HOME"
    assert "6 meetings" in h2h_items[0].reason


def test_streak_difference_produces_evidence():
    evidence = make_evidence(
        home_winning_streak=3, home_losing_streak=0, home_last_10=["W", "W", "W"],
        away_winning_streak=0, away_losing_streak=2, away_last_10=["L", "L"],
    )

    items = build_supporting_evidence(evidence)
    streak_items = [i for i in items if i.title == "Current Streak"]

    assert len(streak_items) == 1
    assert streak_items[0].supports == "HOME"


def test_home_away_split_produces_evidence():
    evidence = make_evidence(
        home_home_wins=8, home_home_played=10,
        away_away_wins=2, away_away_played=10,
    )

    items = build_supporting_evidence(evidence)
    context_items = [i for i in items if i.title == "Home/Away Record"]

    assert len(context_items) == 1
    assert context_items[0].supports == "HOME"
    assert context_items[0].strength == 0.6


# -----------------------------
# No real signal -> omitted, never fabricated
# -----------------------------


def test_tied_signals_produce_no_evidence():
    evidence = make_evidence(
        home_form=["W", "L"], away_form=["L", "W"],
        home_avg_scored=1.5, away_avg_scored=1.5,
        h2h_home_wins=2, h2h_away_wins=2, h2h_matches=4,
    )

    assert build_supporting_evidence(evidence) == []


def test_no_data_at_all_produces_no_evidence():
    """
    The exact shape of a newly-promoted team's evidence dict once the
    temporal boundary correctly excludes everything - must produce an
    honest empty list, not fabricated evidence.
    """

    evidence = make_evidence()

    assert build_supporting_evidence(evidence) == []


def test_zero_head_to_head_history_is_omitted_not_reported_as_zero():
    evidence = make_evidence(h2h_home_wins=0, h2h_away_wins=0, h2h_matches=0)

    items = build_supporting_evidence(evidence)

    assert [i for i in items if i.title == "Head-to-Head"] == []


def test_rest_never_appears_in_supporting_evidence():
    """
    rest_evidence.py is a hardcoded placeholder with no real data -
    including it here would mean fabricating evidence.
    """

    evidence = make_evidence(
        home_form=["W", "W", "W"], away_form=["L", "L", "L"],
    )

    items = build_supporting_evidence(evidence)

    assert all(i.title != "Rest Days" for i in items)
    assert all("rest" not in i.title.lower() for i in items)


# -----------------------------
# Integration: real, temporal-safe evidence dict end-to-end
# -----------------------------


def test_supporting_evidence_reflects_real_temporal_safe_data(real_match_id):
    """
    build_supporting_evidence() introduces no new data source - it
    must only ever reflect what build_evidence() already computed
    under the existing before/exclude_match_id boundary.
    """

    from app.knowledge.knowledge_builder import build_match_profile
    from app.services.match_service import MatchService

    match = MatchService().get_match(real_match_id)
    profile = build_match_profile(match)
    evidence = build_evidence(profile, match_id=match.id, kickoff=match.kickoff)

    items = build_supporting_evidence(evidence)

    assert isinstance(items, list)

    for item in items:
        assert item.supports in ("HOME", "AWAY")
        assert item.strength >= 0
        assert item.reason
