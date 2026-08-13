from app.reasoning.reasoning_rules import (
    evaluate_contradictions,
    evaluate_opportunities,
    evaluate_risks,
    evaluate_strengths,
    evaluate_weaknesses,
)


def make_evidence(
    home_form="WWDLL",
    away_form="LLDWW",
    home_scored=2.0,
    home_conceded=1.0,
    away_scored=1.0,
    away_conceded=1.0,
    home_wins=0,
    away_wins=0,
    home_away=None,
    home_streak=None,
    away_streak=None,
):
    """
    home_away/home_streak/away_streak default to None (i.e. absent
    from the dict) deliberately - this is the exact shape older,
    minimal evidence (or any future caller that doesn't compute
    these) would have, and every rule reading them must degrade
    safely rather than KeyError.
    """

    evidence = {
        "home_team": {
            "form": list(home_form),
            "goals": {
                "avg_goals_scored": home_scored,
                "avg_goals_conceded": home_conceded,
            },
        },
        "away_team": {
            "form": list(away_form),
            "goals": {
                "avg_goals_scored": away_scored,
                "avg_goals_conceded": away_conceded,
            },
        },
        "head_to_head": {
            "home_wins": home_wins,
            "away_wins": away_wins,
        },
    }

    if home_away:
        evidence["home_team"]["home_away"] = home_away.get("home_team", {})
        evidence["away_team"]["home_away"] = home_away.get("away_team", {})

    if home_streak:
        evidence["home_team"]["streak"] = home_streak

    if away_streak:
        evidence["away_team"]["streak"] = away_streak

    return evidence


def streak(winning=0, losing=0):
    return {"winning_streak": winning, "losing_streak": losing}


def home_away_split(wins, played):
    return {"wins": wins, "draws": 0, "losses": played - wins}


def test_strengths_trigger_on_better_form_and_goals():
    evidence = make_evidence(
        home_form="WWWLL",
        away_form="LLLWW",
        home_scored=2.5,
        away_scored=1.0,
    )

    strengths = evaluate_strengths(evidence)

    assert "Home team has stronger recent form." in strengths
    assert "Home team scores more goals on average." in strengths


def test_strengths_empty_when_evenly_matched():
    evidence = make_evidence(
        home_form="WLDWL",
        away_form="WLDWL",
        home_scored=1.5,
        away_scored=1.5,
    )

    assert evaluate_strengths(evidence) == []


def test_weaknesses_trigger_when_home_concedes_more():
    evidence = make_evidence(home_conceded=2.0, away_conceded=1.0)

    weaknesses = evaluate_weaknesses(evidence)

    assert "Home team concedes more goals." in weaknesses


def test_weaknesses_empty_when_home_concedes_fewer():
    evidence = make_evidence(home_conceded=1.0, away_conceded=2.0)

    assert evaluate_weaknesses(evidence) == []


def test_risk_flags_away_team_in_strong_form():
    evidence = make_evidence(away_form="WWWLL")

    risks = evaluate_risks(evidence)

    assert "Away team arrives in strong form." in risks


def test_risk_absent_when_away_form_weak():
    evidence = make_evidence(away_form="LLWDL")

    assert evaluate_risks(evidence) == []


def test_opportunity_flags_favourable_head_to_head():
    evidence = make_evidence(home_wins=4, away_wins=1)

    opportunities = evaluate_opportunities(evidence)

    assert (
        "Historical head-to-head favors the home team."
        in opportunities
    )


def test_opportunity_absent_when_h2h_even_or_unfavourable():
    evidence = make_evidence(home_wins=1, away_wins=3)

    assert evaluate_opportunities(evidence) == []


def test_contradiction_flags_wins_more_but_scores_fewer():
    evidence = make_evidence(
        home_form="WWWLL",
        away_form="LLLWW",
        home_scored=1.0,
        away_scored=2.0,
    )

    contradictions = evaluate_contradictions(evidence)

    assert (
        "Home team wins more often but scores fewer goals."
        in contradictions
    )


def test_contradiction_absent_when_consistent():
    evidence = make_evidence(
        home_form="WWWLL",
        away_form="LLLWW",
        home_scored=2.0,
        away_scored=1.0,
    )

    assert evaluate_contradictions(evidence) == []


# -----------------------------
# Evidence-driven reasoning: streak and home/away split
# -----------------------------


def test_strong_home_record_is_a_strength():
    evidence = make_evidence(
        home_away={"home_team": {"home": home_away_split(wins=8, played=10)}},
    )

    assert "Home team has a strong home-performance record." in evaluate_strengths(evidence)


def test_home_record_below_sample_threshold_is_not_a_strength():
    """
    Two home games is too small a sample to call a "record" - even a
    perfect 2-0 record must not trigger the rule.
    """

    evidence = make_evidence(
        home_form="WLDWL", away_form="WLDWL",  # equal form: no form-based strength
        home_scored=1.5, away_scored=1.5,  # equal goals: no goals-based strength
        home_away={"home_team": {"home": home_away_split(wins=2, played=2)}},
    )

    assert evaluate_strengths(evidence) == []


def test_home_losing_streak_is_a_weakness():
    evidence = make_evidence(home_streak=streak(losing=3))

    assert "Home team is on a losing streak." in evaluate_weaknesses(evidence)


def test_away_winning_streak_is_a_risk():
    evidence = make_evidence(away_streak=streak(winning=4))

    risks = evaluate_risks(evidence)

    assert "Away team is on a strong winning streak." in risks


def test_strong_away_record_is_a_risk():
    evidence = make_evidence(
        home_away={"away_team": {"away": home_away_split(wins=5, played=8)}},
    )

    assert "Away team has a strong away-performance record." in evaluate_risks(evidence)


def test_away_losing_streak_is_an_opportunity():
    evidence = make_evidence(away_streak=streak(losing=3))

    assert "Away team is on a losing streak." in evaluate_opportunities(evidence)


# -----------------------------
# Conflicting evidence
# -----------------------------


def test_h2h_favors_home_but_streak_favors_away_is_flagged_as_contradiction():
    evidence = make_evidence(
        home_wins=4, away_wins=1,
        home_streak=streak(winning=0),
        away_streak=streak(winning=3),
    )

    contradictions = evaluate_contradictions(evidence)

    assert (
        "Historical head-to-head favors the home team, but recent form "
        "favors the away team."
        in contradictions
    )


def test_h2h_favors_away_but_streak_favors_home_is_flagged_as_contradiction():
    evidence = make_evidence(
        home_wins=1, away_wins=4,
        home_streak=streak(winning=3),
        away_streak=streak(winning=0),
    )

    contradictions = evaluate_contradictions(evidence)

    assert (
        "Historical head-to-head favors the away team, but recent form "
        "favors the home team."
        in contradictions
    )


def test_no_contradiction_when_h2h_and_streak_agree():
    evidence = make_evidence(
        home_wins=4, away_wins=1,
        home_streak=streak(winning=3),
        away_streak=streak(winning=0),
    )

    assert evaluate_contradictions(evidence) == []


# -----------------------------
# Strong agreement: multiple independent signals pointing the same way
# -----------------------------


def test_multiple_agreeing_signals_all_surface_as_home_strengths():
    evidence = make_evidence(
        home_form="WWWLL",
        away_form="LLLWW",
        home_scored=2.5,
        away_scored=1.0,
        home_away={"home_team": {"home": home_away_split(wins=8, played=10)}},
        home_streak=streak(winning=4),
    )

    strengths = evaluate_strengths(evidence)

    assert len(strengths) == 4
    assert evaluate_weaknesses(evidence) == []
    assert evaluate_risks(evidence) == []


# -----------------------------
# Sparse / missing evidence degrades safely, never crashes
# -----------------------------


def test_missing_home_away_and_streak_data_does_not_crash_or_fabricate():
    """
    The exact shape of evidence for a match where the temporal
    boundary correctly excluded everything, or where a caller simply
    doesn't compute these fields - must produce no findings, not an
    exception and not an invented one.
    """

    evidence = make_evidence(
        home_form="", away_form="",
        home_scored=0.0, away_scored=0.0,
        home_conceded=0.0, away_conceded=0.0,
    )

    assert evaluate_strengths(evidence) == []
    assert evaluate_weaknesses(evidence) == []
    assert evaluate_risks(evidence) == []
    assert evaluate_opportunities(evidence) == []
    assert evaluate_contradictions(evidence) == []
