from pydantic import BaseModel


class Team(BaseModel):
    id: int

    name: str

    country: str

    league: str

    fifa_rating: float = 0.0

    attack_rating: float = 0.0

    midfield_rating: float = 0.0

    defense_rating: float = 0.0

    goalkeeper_rating: float = 0.0
