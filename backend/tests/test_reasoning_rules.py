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
):
    return {
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
