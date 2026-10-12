import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    FOOTBALL_DATA_API_KEY: str

    def __init__(self):
        api_key = os.getenv("FOOTBALL_DATA_API_KEY")

        if not api_key:
            raise ValueError("FOOTBALL_DATA_API_KEY not found in .env")

        self.FOOTBALL_DATA_API_KEY = api_key


# Built on first use, not at import. Only the sync scripts talk to
# football-data.org, but building this at import time meant merely
# importing FootballDataProvider - which the test suite does - failed
# on any machine without the key, CI included. The missing-key error
# is unchanged; it now surfaces when the provider is actually created.
@lru_cache
def get_settings() -> Settings:
    return Settings()
