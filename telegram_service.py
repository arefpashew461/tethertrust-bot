import os

from telegram import Bot


# =========================
# Telegram Configuration
# =========================

BOT_TOKEN = os.getenv("8616982240:AAFH1oMKar8Ve2Y961qkCm5-9LjVZDDtJLw")

CHANNEL_ID = "@TetherTrust_Official"


# =========================
# Telegram Service
# =========================

class TelegramService:
    """
    مدیریت ارسال پیام‌های TetherTrust به کانال تلگرام
    """

    def __init__(self):

        if not BOT_TOKEN:"8616982240:AAFH1oMKar8Ve2Y961qkCm5-9LjVZDDtJLw"
            raise ValueError(
                "BOT_TOKEN is not set in Railway Variables"
            )

        self.bot = Bot(
            token="8616982240:AAFH1oMKar8Ve2Y961qkCm5-9LjVZDDtJLw"
        )

    async def send_message(self, text):
        """
        ارسال پیام به کانال
        """

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


telegram_service = TelegramService()
