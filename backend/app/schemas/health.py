from pydantic import BaseModel


class HealthStatus(BaseModel):
    platform: str
    version: str
    environment: str
    status: str
    message: str
