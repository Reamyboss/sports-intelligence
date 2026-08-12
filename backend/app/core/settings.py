import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    FOOTBALL_DATA_API_KEY: str

    def __init__(self):
        api_key = os.getenv("FOOTBALL_DATA_API_KEY")

        if not api_key:
            raise ValueError("FOOTBALL_DATA_API_KEY not found in .env")

        self.FOOTBALL_DATA_API_KEY = api_key


settings = Settings()


def get_settings():
    return settings