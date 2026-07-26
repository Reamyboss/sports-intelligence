from fastapi import APIRouter, HTTPException

from app.knowledge.knowledge_builder import build_match_profile
from app.prediction.prediction_engine import predict
from app.services.match_service import get_matches

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"],
)


@router.get("/{match_id}")
def get_prediction(match_id: int):
    matches = get_matches()

    match = next(
        (m for m in matches if m.id == match_id),
        None,
    )

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    profile = build_match_profile(match)

    return predict(profile)