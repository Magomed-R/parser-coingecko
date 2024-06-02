from configparser import ConfigParser

from get_coin import get_coin
from save_coin import save_coin


async def parse_coins(config_url):
    config = ConfigParser()
    config.read(config_url)

    with open(config["default"]["parsing_coins"]) as f:
        coins_urls_list = f.read().split("\n")

    with open(config["default"]["coingecko_off"], "r") as f:
        miss_markets = f.read().split("\n")

    for coin_url in coins_urls_list:
        coin_id = coin_url.split("/")[-1]

        coin = await get_coin(
            coin_id=coin_id,
            headers=config["headers"],
            parse=config["sources"],
            miss_markets=(
                (coin_url in miss_markets) or (config["default"]["markets"] == "off")
            ),
        )

        save_coin(coin, config_url)
