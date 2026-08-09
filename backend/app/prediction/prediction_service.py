from app.prediction.prediction_engine import predict
from app.reasoning.reasoning_engine import build_reasoning


def run_prediction(
    evidence: dict,
    supporting_evidence: list,
):
    """
    Execute the complete prediction pipeline.

    Evidence
        ↓
    Reasoning
        ↓
    Prediction
    """

    reasoning = build_reasoning(
        evidence=evidence,
        supporting_evidence=supporting_evidence,
    )

    return predict(reasoning)