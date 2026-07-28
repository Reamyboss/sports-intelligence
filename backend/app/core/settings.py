import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

        if not self.FOOTBALL_DATA_API_KEY:
            raise ValueError("FOOTBALL_DATA_API_KEY not found in .env")


settings = Settings()


def get_settings():
    return settings