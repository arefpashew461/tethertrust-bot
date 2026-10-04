import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)


CHANNEL_ID = os.getenv(
    "CHANNEL_ID",
    "@TetherTrust_Official"
)


SUPPORT_ID = os.getenv(
    "SUPPORT_ID",
    "@TetherTrust_Support"
)


HISTORY_FILE = "history.json"


PRICE_INTERVAL = 15