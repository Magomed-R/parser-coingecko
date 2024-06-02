import asyncio
import configparser
import json
from get_coin import get_coin
from colorama import Fore, Style
import aiohttp
from get_proxy import Proxy
from save_coin import save_coin

from aiohttp.web_exceptions import HTTPMovedPermanently
from aiohttp.client_exceptions import ClientProxyConnectionError, ClientHttpProxyError

config = configparser.ConfigParser()


async def full_parsing(config_url: str):
    config.read(config_url)
    base_url = "https://api.coingecko.com/api/v3/coins/list"

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, headers=config["headers"]) as response:
            coins = await response.json()

    with open("cache.json", "r") as cache:
        last_coin = json.load(cache)["last_coin"]

    while True:
        config.read(config_url)

        if last_coin >= len(coins) - 1:
            last_coin = 0

        with open(config["default"]["coingecko_off"], "r") as f:
            miss_markets = f.read().split("\n")

        print(
            "{2}. Explore {0} ({1}) page... ".format(
                coins[last_coin]["name"], coins[last_coin]["id"], last_coin
            ),
            end="",
        )

        proxy_class = Proxy("proxy.txt")
        proxy = (
            await proxy_class.get_proxy()
            if config["default"]["use_proxy"] == "on"
            else None
        )

        errors = 0

        while True:
            try:
                coin = await get_coin(
                    coin_id=coins[last_coin]["id"],
                    headers=config["headers"],
                    parse=config["sources"],
                    miss_markets=(
                        (coins[last_coin]["id"] in miss_markets)
                        or (config["default"]["markets"] == "off")
                    ),
                    proxy=proxy,
                )

                break

            except (
                HTTPMovedPermanently,
                ClientProxyConnectionError,
                ClientHttpProxyError,
            ):
                errors += 1
                proxy = (
                    await proxy_class.next_proxy()
                    if config["default"]["use_proxy"] == "on"
                    else None
                )
                print(
                    Fore.YELLOW + "Proxy outdated. Use next proxy..." + Style.RESET_ALL
                )

            except aiohttp.ServerTimeoutError:
                errors += 1
                proxy = (
                    await proxy_class.next_proxy()
                    if config["default"]["use_proxy"] == "on"
                    else None
                )
                print(
                    Fore.YELLOW + "Timeout error. Use next proxy..." + Style.RESET_ALL
                )

            if errors > 30:
                print(Fore.RED + "\nToo many errors. Process dead" + Style.RESET_ALL)
                return exit()

        save_coin(coin=coin, config_url=config_url)

        last_coin += 1

        f = open("cache.json", "r")

        cache = json.load(f)
        cache["last_coin"] = last_coin
        cache["coin_name"] = coins[last_coin]["name"]
        cache["coin_id"] = coins[last_coin]["id"]

        f = open("cache.json", "w")
        json.dump(cache, f)
        f.close()

        print(Fore.GREEN + "successfully!" + Style.RESET_ALL)


if __name__ == "__main__":
    asyncio.run(full_parsing("module-1.ini"))
