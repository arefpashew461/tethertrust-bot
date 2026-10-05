import aiohttp
import asyncio
import time
from logger import logger


TIMEOUT = aiohttp.ClientTimeout(total=15)


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
            headers={
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "User-Agent": "TetherTrustBot/1.0",
            },
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

                price = int(
                    float(item["price"])
                )

                logger.info(
                    "Bitpin LIVE price: %s",
                    price
                )

                return {
                    "name": "Bitpin",
                    "price": price,
                }

        logger.warning(
            "Bitpin: USDT_IRT not found"
        )

    except Exception as e:

        logger.exception(
            "Bitpin error: %s",
            e
        )

    return None


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
            headers={
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "User-Agent": "TetherTrustBot/1.0",
            },
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
            headers={
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "User-Agent": "TetherTrustBot/1.0",
            },
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

                price = item[
                    "margin_config"
                ][
                    "pair"
                ][
                    "last_trade_price"
                ]

                price = int(float(price))

                logger.info(
                    "Tabdeal LIVE price: %s",
                    price
                )

                return {
                    "name": "Tabdeal",
                    "price": price,
                }

        logger.warning(
            "Tabdeal: USDT/IRT not found"
        )

    except Exception as e:

        logger.exception(
            "Tabdeal error: %s",
            e
        )

    return None


async def collect_prices():

    async with aiohttp.ClientSession() as session:

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

            if price and price > 0:

                prices.append(item)

    logger.info(
        "LIVE PRICE SOURCES: %s",
        prices
    )

    return prices


async def get_average_price():

    sources = await collect_prices()

    if not sources:

        logger.error(
            "NO PRICE SOURCES AVAILABLE"
        )

        return None

    values = [
        item["price"]
        for item in sources
    ]

    initial_average = (
        sum(values) / len(values)
    )

    logger.info(
        "Initial average: %s",
        initial_average
    )

    valid = []

    for item in sources:

        difference = (
            abs(
                item["price"]
                - initial_average
            )
            / initial_average
        )

        logger.info(
            "%s difference: %.3f%%",
            item["name"],
            difference * 100
        )

        if difference < 0.01:
            valid.append(item)

    if valid:

        average = int(
            sum(
                item["price"]
                for item in valid
            )
            / len(valid)
        )

    else:

        average = int(
            initial_average
        )

    result = {
        "price": average,
        "sources": [
            item["name"]
            for item in valid
        ],
    }

    logger.info(
        "FINAL LIVE PRICE: %s | SOURCES: %s",
        result["price"],
        result["sources"]
    )

    return result
