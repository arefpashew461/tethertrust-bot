import os

from telegram import Bot


# =========================
# Telegram Configuration
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@TetherTrust_Official"


# =========================
# Telegram Service
# =========================

class TelegramService:

    def __init__(self):

        if not BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN is not set in Railway Variables"
            )

        self.bot = Bot(
            token=BOT_TOKEN
        )

    async def send_message(self, text):

        try:

            await self.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text
            )

            print("Telegram message sent successfully.")

            return True

        except Exception as error:

            print("Telegram Error:", error)

            return False


# =========================
# Create Telegram Service
# =========================

telegram_service = TelegramService()
