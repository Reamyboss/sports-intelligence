from pydantic import BaseModel


class Evidence(BaseModel):
    """
    Represents one piece of evidence used by the reasoning engine.
    """

    title: str

    supports: str

    strength: float

    reason: str