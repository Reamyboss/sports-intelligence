from pydantic import BaseModel


class Team(BaseModel):
    """
    Represents the permanent identity of a football club.
    """

    id: int

    name: str

    country: str

    league: str

    stadium: str

    manager: str
