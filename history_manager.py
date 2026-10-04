import json
import os

from datetime import datetime, timezone, timedelta

from config import HISTORY_FILE



# -------------------------
# Time Tehran
# -------------------------

TEHRAN = timezone(
    timedelta(
        hours=3,
        minutes=30
    )
)



def now_tehran():

    return datetime.now(
        TEHRAN
    )



# -------------------------
# Load History
# -------------------------

def load_history():

    if not os.path.exists(
        HISTORY_FILE
    ):

        return []


    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )


    except Exception:

        return []



# -------------------------
# Save History
# -------------------------

def save_history(
    buy_price,
    sell_price,
    sources,
    change_amount,
    change_percent
):

    history = load_history()


    now = now_tehran()


    record = {

        "date":
            now.strftime(
                "%Y-%m-%d"
            ),


        "time":
            now.strftime(
                "%H:%M"
            ),


        "buy":
            buy_price,


        "sell":
            sell_price,


        "change_amount":
            change_amount,


        "change_percent":
            round(
                change_percent,
                2
            ),


        "sources":
            sources

    }


    history.append(
        record
    )


    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=4
        )


    return record



# -------------------------
# Today History
# -------------------------

def get_today_history():

    today = now_tehran().strftime(
        "%Y-%m-%d"
    )


    return [

        item

        for item in load_history()

        if item.get(
            "date"
        ) == today

    ]



# -------------------------
# Daily Report
# -------------------------

def get_daily_stats():

    data = get_today_history()


    if not data:

        return None



    prices = [

        item["buy"]

        for item in data

    ]



    first = prices[0]

    last = prices[-1]



    change = last - first


    percent = (
        change
        /
        first
        *
        100
    )


    return {

        "first":
            first,


        "last":
            last,


        "high":
            max(prices),


        "low":
            min(prices),


        "average":
            int(
                sum(prices)
                /
                len(prices)
            ),


        "change":
            change,


        "percent":
            percent

    }