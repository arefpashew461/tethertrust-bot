from telegram import Bot

from config import (
    BOT_TOKEN,
    CHANNEL_ID
)



class TelegramService:
    """
    مدیریت ارسال پیام‌های TetherTrust به کانال
    """

    def __init__(self):

        self.bot = Bot(
            token=BOT_TOKEN
        )



    async def send_message(
        self,
        text
    ):
        """
        ارسال پیام به کانال تلگرام
        """

        try:

            await self.bot.send_message(

                chat_id=CHANNEL_ID,

                text=text

            )


            return True



        except Exception as error:


            print(
                "Telegram Error:",
                error
            )


            return False




telegram_service = TelegramService()