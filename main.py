import asyncio

from datetime import timezone, timedelta


from apscheduler.schedulers.asyncio import AsyncIOScheduler


from config import PRICE_INTERVAL


from price_service import get_average_price


from history_manager import (
    save_history,
    get_daily_stats
)


from alerts import create_alert


from morning_messages import get_morning_message


from telegram_service import telegram_service


from logger import logger


import jdatetime



# -------------------------
# Tehran Time
# -------------------------

TEHRAN = timezone(
    timedelta(
        hours=3,
        minutes=30
    )
)



# -------------------------
# Last Price
# -------------------------

last_price = None



# -------------------------
# Send Price Report
# -------------------------

async def send_price_report():

    global last_price


    try:

        result = await get_average_price()


        if not result:

            logger.warning(
                "No price received"
            )

            return
           
            
        current_price = result["price"]


        sources = result["sources"]



        change_amount = 0

        change_percent = 0

        change_text = f"{change_amount:+,}\n({change_percent:+.2f}%)"



        if last_price:


            change_amount = (
                current_price
                -
                last_price
            )


            change_percent = (

                change_amount

                /

                last_price

                *

                100

            )

        change_text = f"{change_amount:+,                  }\n({change_percent:+.2f}%)"



        sell_price = (
            current_price
            +
            150
        )
        buy_price = current_price



        save_history(

            current_price,

            sell_price,

            sources,

            change_amount,

            change_percent

        )



        message = f"""
💠 TETHERTRUST | مرجع تتر

┏━━━━━━━━━━┓
💵 خرید:
{buy_price:,} تومان
🔵 فروش:
{sell_price:,} تومان

📈 روند:
{change_text}

🕒 {now.strftime("%H:%M")}
📅 {jalali_date}

┗━━━━━━━━━━┛
"""


        await telegram_service.send_message(
            message
        )


        if last_price:

            alert = create_alert(

                current_price,

                last_price

            )


            if alert:

                await telegram_service.send_message(
                    alert
                )



        last_price = current_price



        logger.info(
            "Price sent successfully"
        )


    except Exception as error:


        logger.error(
            error
        )



def datetime_now():

    from datetime import datetime

    now = datetime.now(
        TEHRAN
    )


    jalali = jdatetime.datetime.fromgregorian(
        datetime=now
    )


    return (
        f"{jalali.strftime('%Y/%m/%d')}"
        f" - "
        f"{now.strftime('%H:%M')}"
    )
    
async def send_price_report():

    global last_price

    try:

        result = await get_average_price()

        if not result:

            logger.warning(
                "No price received"
            )

            return


        current_price = result["price"]

        sources = result["sources"]


        change_amount = 0

        change_percent = 0


        if last_price:

            change_amount = (
                current_price
                -
                last_price
            )


            change_percent = (

                change_amount

                /

                last_price

                *

                100

            )


        change_text = (
            f"{change_amount:+,}\n"
            f"({change_percent:+.2f}%)"
        )


        sell_price = (
            current_price
            +
            150
        )


        buy_price = current_price


        save_history(

            current_price,

            sell_price,

            sources,

            change_amount,

            change_percent

        )


        now = datetime_now()


        message = f"""
 💠 TETHERTRUST | مرجع تتر

┏━━━━━━━━━━┓
💵 خرید:
{buy_price:,} تومان
🔵 فروش:
{sell_price:,} تومان

📈 روند بازار:
{change_text}

🕒 {now.split(" - ")[1]}
📅 {now.split(" - ")[0]}

┗━━━━━━━━━━┛
"""


        await telegram_service.send_message(
            message
        )


        if last_price:

            alert = create_alert(

                current_price,

                last_price

            )


            if alert:

                await telegram_service.send_message(
                    alert
                )


        last_price = current_price


        logger.info(
            "Price sent successfully"
        )


    except Exception as error:

        logger.error(
            error
        )
 # -------------------------
# Morning Report
# -------------------------

async def send_morning_report():

    try:

        message = f"""
💠 TETHERTRUST | مرجع تتر

┏━━━━━━━━━━┓

{get_morning_message()}

🕒 شروع روز معاملاتی
📅 TetherTrust

⚜️ اعتبار، ارزِ ماندگارِ ماست.

📢 کانال رسمی: @TetherTrust_Official
🎧 پشتیبانی: @TetherTrust_Support

┗━━━━━━━━━━┛
"""

        await telegram_service.send_message(
            message
        )

        logger.info(
            "Morning report sent"
        )


    except Exception as error:

        logger.exception(
            error
        )



# -------------------------
# Night Report
# -------------------------

async def send_night_report():

    try:

        stats = get_daily_stats()


        if not stats:

            logger.warning(
                "No daily stats available"
            )

            return


        message = f"""
💠 TETHERTRUST | گزارش روزانه

┏━━━━━━━━━━┓

📊 آمار امروز بازار تتر

💵 شروع:
{stats["first"]:,} تومان

🔵 پایان:
{stats["last"]:,} تومان

⬆️ بالاترین:
{stats["high"]:,} تومان

⬇️ پایین‌ترین:
{stats["low"]:,} تومان

📈 تغییر روز:
{stats["change"]:+,} تومان

({stats["percent"]:+.2f}%)

📌 میانگین:
{stats["average"]:,} تومان

⚜️ اعتبار، ارزِ ماندگارِ ماست.

📢 کانال رسمی: @TetherTrust_Official
🎧 پشتیبانی: @TetherTrust_Support

┗━━━━━━━━━━┛
"""


        await telegram_service.send_message(
            message
        )


        logger.info(
            "Night report sent"
        )


    except Exception as error:

        logger.exception(
            error
        )
  # -------------------------
# Main Runner
# -------------------------

async def main():

    logger.info(
        "Starting TetherTrust Bot..."
    )


    scheduler = AsyncIOScheduler(
        timezone=TEHRAN
    )


    scheduler.add_job(
        send_price_report,
        "interval",
        minutes=15
    )


    scheduler.add_job(
        send_morning_report,
        "cron",
        hour=7,
        minute=59
    )


    scheduler.add_job(
        send_night_report,
        "cron",
        hour=23,
        minute=59
    )


    scheduler.start()


    await send_price_report()


    logger.info(
        "TetherTrust Bot is running"
    )


    while True:

        await asyncio.sleep(
            60
        )



# -------------------------
# Start Program
# -------------------------

if __name__ == "__main__":

    asyncio.run(
        main()
    )