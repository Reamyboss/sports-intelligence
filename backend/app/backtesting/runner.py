"""
Runs both the baseline and current prediction systems against real
historical matches, treating each one as if it had not happened yet.

Every piece of evidence is built through the real, unmodified
production functions (build_match_profile, build_evidence,
build_reasoning, build_supporting_evidence) with the match's own
before=kickoff / exclude_match_id=match.id boundary - the same
boundary GET /prediction/{id} uses live. The actual result is only
read out afterward, for scoring - never before or during prediction.
"""

from dataclasses import dataclass

from app.backtesting.baseline import (
    calculate_confidence_baseline,
    predict_match_winner_baseline,
)
from app.backtesting.dataset import actual_result
from app.confidence.confidence_engine import calculate_confidence
from app.evidence.evidence_builder import build_evidence, build_supporting_evidence
from app.knowledge.knowledge_builder import build_match_profile
from app.models.match import Match
from app.prediction.prediction_rules import predict_match_winner
from app.reasoning.reasoning_engine import build_reasoning


@dataclass
class BacktestResult:
    match_id: int
    competition: str
    kickoff: object
    home_team: str
    away_team: str
    actual: str

    baseline_prediction: str
    baseline_probability: float
    baseline_confidence: float

    current_prediction: str
    current_probability: float
    current_confidence: float

    evidence_count: int
    home_support: int
    away_support: int


def run_single_backtest(match: Match) -> BacktestResult:
    """
    Predicts `match` as if it had not been played yet, then reveals
    the real result only for the caller to score afterward.
    """

    profile = build_match_profile(match)

    # The temporal boundary: only matches strictly before this one's
    # kickoff, and never this match itself.
    evidence = build_evidence(profile, match_id=match.id, kickoff=match.kickoff)

    supporting_evidence = build_supporting_evidence(evidence)

    reasoning = build_reasoning(evidence=evidence, supporting_evidence=supporting_evidence)

    baseline_prediction, baseline_probability = predict_match_winner_baseline(reasoning)
    baseline_confidence = calculate_confidence_baseline(reasoning, baseline_probability)

    current_prediction, current_probability = predict_match_winner(reasoning)
    current_confidence = calculate_confidence(reasoning, current_probability)

    home_support = sum(1 for item in supporting_evidence if item.supports == "HOME")
    away_support = sum(1 for item in supporting_evidence if item.supports == "AWAY")

    # The real result is read only now, after both predictions exist.
    result = actual_result(match)

    return BacktestResult(
        match_id=match.id,
        competition=match.competition,
        kickoff=match.kickoff,
        home_team=match.home_team,
        away_team=match.away_team,
        actual=result,
        baseline_prediction=baseline_prediction,
        baseline_probability=baseline_probability,
        baseline_confidence=baseline_confidence,
        current_prediction=current_prediction,
        current_probability=current_probability,
        current_confidence=current_confidence,
        evidence_count=len(supporting_evidence),
        home_support=home_support,
        away_support=away_support,
    )


def run_backtest(matches: list[Match]) -> list[BacktestResult]:
    return [run_single_backtest(match) for match in matches]
