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


# =========================
# Tehran Time
# =========================

TEHRAN = timezone(
    timedelta(
        hours=3,
        minutes=30
    )
)


# =========================
# Last Price
# =========================

last_price = None


# =========================
# Date / Time
# =========================

def get_tehran_datetime():

    from datetime import datetime

    now = datetime.now(TEHRAN)

    jalali = jdatetime.datetime.fromgregorian(
        datetime=now
    )

    return now, jalali


# =========================
# Send Price Report
# =========================

async def send_price_report():

    global last_price

    try:

        logger.info("Fetching latest price...")

        result = await get_average_price()

        if not result:
            logger.warning("No price received")
            return

        current_price = result["price"]
        sources = result.get("sources", [])

        logger.info(
            f"Latest price received: {current_price}"
        )

        # -------------------------
        # Calculate change
        # -------------------------

        change_amount = 0
        change_percent = 0

        if last_price:

            change_amount = (
                current_price - last_price
            )

            change_percent = (
                change_amount
                / last_price
                * 100
            )

        change_text = (
            f"{change_amount:+,}\n"
            f"({change_percent:+.2f}%)"
        )

        # -------------------------
        # Buy / Sell
        # -------------------------

        buy_price = current_price

        sell_price = current_price + 150

        # -------------------------
        # Save history
        # -------------------------

        save_history(
            current_price,
            sell_price,
            sources,
            change_amount,
            change_percent
        )

        # -------------------------
        # Tehran date/time
        # -------------------------

        now, jalali = get_tehran_datetime()

        # -------------------------
        # Telegram message
        # -------------------------

        message = f"""
💠 TETHERTRUST | مرجع تتر

┏━━━━━━━━━━┓

💵 خرید:
{buy_price:,} تومان

🔵 فروش:
{sell_price:,} تومان

📈 روند بازار:
{change_text}

🕒 {now.strftime("%H:%M")}
📅 {jalali.strftime("%Y/%m/%d")}

┗━━━━━━━━━━┛
"""

        sent = await telegram_service.send_message(
            message
        )

        if not sent:

            logger.error(
                "Telegram message was not sent"
            )

            return

        # -------------------------
        # Price alert
        # -------------------------

        if last_price:

            alert = create_alert(
                current_price,
                last_price
            )

            if alert:

                await telegram_service.send_message(
                    alert
                )

        # -------------------------
        # Update last price
        # -------------------------

        last_price = current_price

        logger.info(
            f"Price report sent successfully: {current_price}"
        )

    except Exception as error:

        logger.exception(
            f"Price report error: {error}"
        )


# =========================
# Morning Report
# =========================

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


# =========================
# Night Report
# =========================

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


# =========================
# Main Runner
# =========================

async def main():

    logger.info(
        "Starting TetherTrust Bot..."
    )

    scheduler = AsyncIOScheduler(
        timezone=TEHRAN
    )

    # -------------------------
    # Price every 15 minutes
    # -------------------------

    scheduler.add_job(
        send_price_report,
        "interval",
        minutes=15,
        max_instances=1,
        coalesce=True
    )

    # -------------------------
    # Morning report
    # -------------------------

    scheduler.add_job(
        send_morning_report,
        "cron",
        hour=7,
        minute=59
    )

    # -------------------------
    # Night report
    # -------------------------

    scheduler.add_job(
        send_night_report,
        "cron",
        hour=23,
        minute=59
    )

    scheduler.start()

    logger.info(
        "Scheduler started successfully"
    )

    # Send first price immediately

    await send_price_report()

    logger.info(
        "TetherTrust Bot is running"
    )

    while True:

        await asyncio.sleep(60)


# =========================
# Start Program
# =========================

if __name__ == "__main__":

    asyncio.run(
        main()
)
