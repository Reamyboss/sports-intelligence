from pydantic import BaseModel


class Competition(BaseModel):

    id: int

    name: str

    country: str

    season: str
