import aiohttp
import asyncio
import time
from logger import logger


REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15)

HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
    "User-Agent": "TetherTrust-Bot/1.0",
}


async def get_bitpin_price(session):
    try:
        url = "https://api.bitpin.ir/v1/mkt/markets/"

        # جلوگیری از cache
        params = {
            "_t": str(int(time.time()))
        }

        async with session.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
            headers=HEADERS,
        ) as response:

            response.raise_for_status()
            data = await response.json(content_type=None)

        for item in data.get("results", []):

            if item.get("code") == "USDT_IRT":

                price = item.get("price")

                if price is None:
                    logger.warning("Bitpin: price is missing")
                    return None

                result = {
                    "name": "Bitpin",
                    "price": int(float(price)),
                }

                logger.info("Bitpin price: %s", result["price"])

                return result

        logger.warning("Bitpin: USDT_IRT not found")

    except Exception as e:
        logger.error("Bitpin error: %s", e)

    return None


async def get_nobitex_price(session):
    try:
        url = "https://apiv2.nobitex.ir/market/stats"

        params = {
            "srcCurrency": "usdt",
            "dstCurrency": "rls",
            "_t": str(int(time.time())),
        }

        async with session.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
            headers=HEADERS,
        ) as response:

            response.raise_for_status()
            data = await response.json(content_type=None)

        latest = data["stats"]["usdt-rls"]["latest"]

        # Nobitex قیمت را ریال می‌دهد
        # تبدیل ریال به تومان
        price = int(float(latest) / 10)

        result = {
            "name": "Nobitex",
            "price": price,
        }

        logger.info("Nobitex price: %s", price)

        return result

    except Exception as e:
        logger.error("Nobitex error: %s", e)

    return None


async def get_tabdeal_price(session):
    try:
        url = "https://api-web.tabdeal.org/markets"

        params = {
            "_t": str(int(time.time()))
        }

        async with session.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
            headers=HEADERS,
        ) as response:

            response.raise_for_status()
            data = await response.json(content_type=None)

        for item in data.get("markets", []):

            first = item.get("first_currency", {})
            second = item.get("second_currency", {})

            if (
                first.get("symbol") == "USDT"
                and second.get("symbol") == "IRT"
            ):

                margin_config = item.get("margin_config", {})
                pair = margin_config.get("pair", {})

                last_trade_price = pair.get("last_trade_price")

                if last_trade_price is None:
                    logger.warning(
                        "Tabdeal: last_trade_price is missing"
                    )
                    return None

                price = int(float(last_trade_price))

                result = {
                    "name": "Tabdeal",
                    "price": price,
                }

                logger.info("Tabdeal price: %s", price)

                return result

        logger.warning("Tabdeal: USDT/IRT market not found")

    except Exception as e:
        logger.error("Tabdeal error: %s", e)

    return None


async def collect_prices():

    async with aiohttp.ClientSession(
        timeout=REQUEST_TIMEOUT,
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

            if price and price > 0:

                prices.append(item)

    logger.info(
        "Collected prices: %s",
        prices
    )

    return prices


async def get_average_price():

    sources = await collect_prices()

    logger.info(
        "PRICE SOURCES: %s",
        sources
    )

    if not sources:
        logger.error(
            "No valid price sources available!"
        )
        return None

    # حداقل یک قیمت داریم
    values = [
        item["price"]
        for item in sources
    ]

    # میانگین اولیه
    average = sum(values) / len(values)

    logger.info(
        "Initial average: %s",
        average
    )

    # حذف قیمت‌هایی که بیشتر از 1٪
    # با میانگین اختلاف دارند
    valid = []

    for item in sources:

        difference = abs(
            item["price"] - average
        ) / average

        if difference < 0.01:

            valid.append(item)

        else:

            logger.warning(
                "%s rejected: price=%s difference=%.2f%%",
                item["name"],
                item["price"],
                difference * 100,
            )

    # اگر حداقل یک منبع معتبر داریم
    if valid:

        average = int(
            sum(
                item["price"]
                for item in valid
            )
            / len(valid)
        )

    else:
        # اگر فیلتر 1٪ همه را حذف کرد،
        # از میانگین اولیه استفاده کن
        average = int(average)

        logger.warning(
            "No sources passed 1%% filter. "
            "Using initial average: %s",
            average
        )

    result = {
        "price": average,
        "sources": [
            item["name"]
            for item in valid
        ],
    }

    logger.info(
        "FINAL PRICE: %s | SOURCES: %s",
        result["price"],
        result["sources"],
    )

    return result
