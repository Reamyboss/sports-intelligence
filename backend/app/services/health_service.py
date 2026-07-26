from app.config import settings


def get_health():
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "message": "Foundation initialized successfully.",
    }
