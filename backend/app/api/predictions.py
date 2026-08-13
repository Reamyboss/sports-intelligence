from fastapi import APIRouter, HTTPException

from app.evidence.evidence_builder import build_evidence, build_supporting_evidence
from app.knowledge.knowledge_builder import build_match_profile
from app.prediction.prediction_models import PredictionResult
from app.prediction.prediction_service import run_prediction
from app.services.match_service import MatchService

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"],
)

match_service = MatchService()


@router.get("/{match_id}", response_model=PredictionResult)
def get_prediction(match_id: int) -> PredictionResult:
    """
    Generate an AI prediction for a specific match.
    """

    match = match_service.get_match(match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    profile = build_match_profile(match)

    evidence = build_evidence(
        profile,
        match_id=match.id,
        kickoff=match.kickoff,
    )

    supporting_evidence = build_supporting_evidence(evidence)

    prediction = run_prediction(
        evidence=evidence,
        supporting_evidence=supporting_evidence,
    )

    return prediction