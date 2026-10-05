from telegram import Bot

from config import 'AAFH1oMKar8Ve2Y961qkCm5-9LjVZDDtJLw'
    CHANNEL_ID '@TetherTrust_Official'



class TelegramService:
    """
    مدیریت ارسال پیام‌های TetherTrust به کانال
    """

    def __init__(self):

        self.bot = Bot(
            token='AAFH1oMKar8Ve2Y961qkCm5-9LjVZDDtJLw'
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

                chat_id='@TetherTrust_Official'

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
