from dataclasses import dataclass

from app.domain.match import Match


@dataclass(slots=True)
class KnowledgeProfile:
    match: Match

    home_advantage: bool

    recent_form: dict

    head_to_head: dict

    confidence_inputs: dict

    metadata: dict