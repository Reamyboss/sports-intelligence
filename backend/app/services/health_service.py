from app.config import settings
from app.schemas.health import HealthStatus


def get_health() -> HealthStatus:
    return HealthStatus(
        platform=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        status="running",
        message="Foundation initialized successfully.",
    )
