import aiohttp
import asyncio



async def get_bitpin_price(session):

    try:

        url = "https://api.bitpin.ir/v1/mkt/markets/"

        async with session.get(
            url,
            timeout=15
        ) as response:

            data = await response.json()


        for item in data.get("results", []):

            if item.get("code") == "USDT_IRT":

                return {
                    "name": "Bitpin",
                    "price": int(float(item["price"]))
                }


    except Exception:

        return None



async def get_nobitex_price(session):

    try:

        url = (
            "https://apiv2.nobitex.ir/market/"
            "stats?srcCurrency=usdt&dstCurrency=rls"
        )


        async with session.get(
            url,
            timeout=15
        ) as response:

            data = await response.json()


        price = int(
            data["stats"]["usdt-rls"]["latest"]
        )


        return {
            "name": "Nobitex",
            "price": price // 10
        }


    except Exception:

        return None



async def get_tabdeal_price(session):

    try:

        url = "https://api-web.tabdeal.org/markets"


        async with session.get(
            url,
            timeout=15
        ) as response:

            data = await response.json()


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

                price = item["margin_config"]["pair"]["last_trade_price"]

                return {
                    "name": "Tabdeal",
                    "price": int(float(price))
                }


    except Exception:

        return None



async def collect_prices():

    async with aiohttp.ClientSession() as session:

        results = await asyncio.gather(

            get_bitpin_price(session),

            get_tabdeal_price(session),

            get_nobitex_price(session),

            return_exceptions=True
        )


    prices = []


    for item in results:

        if isinstance(item, dict):

            if item.get("price"):

                prices.append(item)


    return prices



async def get_average_price():

    sources = await collect_prices()

    print("PRICE SOURCES:", sources)
        
    if not sources:

        return None


    values = [

        item["price"]

        for item in sources

    ]


    average = int(
        sum(values)
        /
        len(values)
    )


    valid = [

        item

        for item in sources

        if abs(
            item["price"] - average
        )
        /
        average
        < 0.01

    ]


    if valid:

        average = int(
            sum(
                item["price"]
                for item in valid
            )
            /
            len(valid)
        )
              

    print("PRICE TEST:", average, sources)


    
    return {

        "price": average,

        "sources": [

            item["name"]

            for item in valid

        ]

    }