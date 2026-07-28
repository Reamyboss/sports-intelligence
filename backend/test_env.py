from dotenv import load_dotenv
import os

load_dotenv()

print("API KEY:", os.getenv("FOOTBALL_DATA_API_KEY"))