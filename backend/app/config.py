from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "Sports Intelligence Platform"
    APP_VERSION: str = "0.0.1"

    # Set ENVIRONMENT=production on the deployed service. The default
    # stays "development" so a developer running locally is never
    # misreported as production - which means a deployment that never
    # sets it reports itself as development, as ours currently does.
    ENVIRONMENT: str = "development"

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://sports-intelligence-svpl.onrender.com",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() == "production"

    @property
    def DEBUG(self) -> bool:
        """
        Derived, never configured independently.

        This was a separate flag defaulting to True, which allowed
        ENVIRONMENT=production and DEBUG=True to be set at the same
        time and disagree silently. Nothing in the application reads
        it today - FastAPI is constructed without debug, and the
        unhandled-exception handler returns a fixed message rather
        than a traceback - so no debug behaviour is or was exposed in
        production. Deriving it keeps that true if something starts
        reading it.
        """

        return not self.is_production


settings = Settings()
