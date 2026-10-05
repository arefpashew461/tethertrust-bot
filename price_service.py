import aiohttp
import asyncio
import time

from logger import logger


# ============================================================
# TetherTrust - Price Service
# ============================================================

print("🔥 NEW PRICE_SERVICE.PY LOADED 🔥")


TIMEOUT = aiohttp.ClientTimeout(total=15)


HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
    "User-Agent": "TetherTrustBot/1.0",
}


# ============================================================
# Bitpin
# ============================================================

async def get_bitpin_price(session):

    try:

        url = "https://api.bitpin.ir/v1/mkt/markets/"

        params = {
            "_t": str(time.time())
        }

        async with session.get(
            url,
            params=params,
            timeout=TIMEOUT,
            headers=HEADERS,
        ) as response:

            logger.info(
                "Bitpin HTTP status: %s",
                response.status
            )

            response.raise_for_status()

            data = await response.json(
                content_type=None
            )

        for item in data.get("results", []):

            if item.get("code") == "USDT_IRT":

                price = item.get("price")

                if price is None:
                    logger.warning(
                        "Bitpin price is missing"
                    )
                    return None

                price = int(float(price))

                logger.info(
                    "Bitpin LIVE price: %s",
                    price
                )

                return {
                    "name": "Bitpin",
                    "price": price,
                }

        logger.warning(
            "Bitpin: USDT_IRT market not found"
        )

    except Exception as e:

        logger.exception(
            "Bitpin error: %s",
            e
        )

    return None


# ============================================================
# Nobitex
# ============================================================

async def get_nobitex_price(session):

    try:

        url = "https://apiv2.nobitex.ir/market/stats"

        params = {
            "srcCurrency": "usdt",
            "dstCurrency": "rls",
            "_t": str(time.time()),
        }

        async with session.get(
            url,
            params=params,
            timeout=TIMEOUT,
            headers=HEADERS,
        ) as response:

            logger.info(
                "Nobitex HTTP status: %s",
                response.status
            )

            response.raise_for_status()

            data = await response.json(
                content_type=None
            )

        latest = data["stats"]["usdt-rls"]["latest"]

        # Nobitex قیمت را به ریال برمی‌گرداند
        # تبدیل ریال به تومان
        price = int(
            float(latest) / 10
        )

        logger.info(
            "Nobitex LIVE price: %s",
            price
        )

        return {
            "name": "Nobitex",
            "price": price,
        }

    except Exception as e:

        logger.exception(
            "Nobitex error: %s",
            e
        )

    return None


# ============================================================
# Tabdeal
# ============================================================

async def get_tabdeal_price(session):

    try:

        url = "https://api-web.tabdeal.org/markets"

        params = {
            "_t": str(time.time())
        }

        async with session.get(
            url,
            params=params,
            timeout=TIMEOUT,
            headers=HEADERS,
        ) as response:

            logger.info(
                "Tabdeal HTTP status: %s",
                response.status
            )

            response.raise_for_status()

            data = await response.json(
                content_type=None
            )

        for item in data.get("markets", []):

            first = item.get(
                "first_currency",
                {}
            )

            second = item.get(
                "second_currency",
                {}
            )

            if (
                first.get("symbol") == "USDT"
                and
                second.get("symbol") == "IRT"
            ):

                margin_config = item.get(
                    "margin_config",
                    {}
                )

                pair = margin_config.get(
                    "pair",
                    {}
                )

                last_trade_price = pair.get(
                    "last_trade_price"
                )

                if last_trade_price is None:

                    logger.warning(
                        "Tabdeal last_trade_price missing"
                    )

                    return None

                price = int(
                    float(last_trade_price)
                )

                logger.info(
                    "Tabdeal LIVE price: %s",
                    price
                )

                return {
                    "name": "Tabdeal",
                    "price": price,
                }

        logger.warning(
            "Tabdeal: USDT/IRT market not found"
        )

    except Exception as e:

        logger.exception(
            "Tabdeal error: %s",
            e
        )

    return None


# ============================================================
# Collect all prices
# ============================================================

async def collect_prices():

    logger.info(
        "========== FETCHING LIVE PRICES =========="
    )

    async with aiohttp.ClientSession(
        timeout=TIMEOUT,
        headers=HEADERS,
    ) as session:

        results = await asyncio.gather(

            get_bitpin_price(session),

            get_nobitex_price(session),

            get_tabdeal_price(session),

            return_exceptions=True,
        )

    prices = []

    for item in results:

        if isinstance(item, Exception):

            logger.error(
                "Price source exception: %s",
                item
            )

            continue

        if isinstance(item, dict):

            price = item.get("price")

            if (
                isinstance(price, (int, float))
                and price > 0
            ):

                prices.append(item)

    logger.info(
        "LIVE PRICE SOURCES: %s",
        prices
    )

    return prices


# ============================================================
# Calculate average
# ============================================================

async def get_average_price():

    sources = await collect_prices()

    if not sources:

        logger.error(
            "❌ NO PRICE SOURCES AVAILABLE"
        )

        return None

    # --------------------------------------------------------
    # Initial average
    # --------------------------------------------------------

    values = [
        item["price"]
        for item in sources
    ]

    initial_average = (
        sum(values)
        /
        len(values)
    )

    logger.info(
        "Initial average: %.2f",
        initial_average
    )

    # --------------------------------------------------------
    # Remove abnormal prices
    # Maximum allowed difference = 1%
    # --------------------------------------------------------

    valid = []

    for item in sources:

        difference = (
            abs(
                item["price"]
                -
                initial_average
            )
            /
            initial_average
        )

        logger.info(
            "%s difference: %.3f%%",
            item["name"],
            difference * 100
        )

        if difference < 0.01:

            valid.append(item
