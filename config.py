import os

from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SOURCE_CHANNEL_ID = os.getenv("SOURCE_CHANNEL_ID")
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")

PROMO_CHANNEL_NAME = os.getenv("PROMO_CHANNEL_NAME")
PROMO_CHANNEL_URL = os.getenv("PROMO_CHANNEL_URL")

SEARCH_WINDOW_HOURS = int(os.getenv("SEARCH_WINDOW_HOURS"))
COOLDOWN_HOURS = int(os.getenv("COOLDOWN_HOURS"))
REACTION_MULTIPLIER = int(os.getenv("REACTION_MULTIPLIER"))

SESSION_NAME = os.getenv("SESSION_NAME")
