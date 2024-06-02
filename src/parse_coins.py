from configparser import ConfigParser

from get_coin import get_coin
from get_proxy import Proxy
from save_coin import save_coin
from colorama import Fore, Style

from aiohttp.web_exceptions import HTTPMovedPermanently
from aiohttp.client_exceptions import ClientProxyConnectionError, ClientHttpProxyError
from aiohttp import ServerTimeoutError


async def parse_coins(config_url):
    config = ConfigParser()
    config.read(config_url)

    with open(config["default"]["parsing_coins"]) as f:
        coins_urls_list = f.read().split("\n")

    with open(config["default"]["coingecko_off"], "r") as f:
        miss_markets = f.read().split("\n")

    proxy_class = Proxy("proxy.txt")
    proxy = (
        await proxy_class.get_proxy()
        if config["default"]["use_proxy"] == "on"
        else None
    )

    for coin_url in coins_urls_list:
        coin_id = coin_url.split("/")[-1]

        errors = 0

        while True:
            try:
                coin = await get_coin(
                    coin_id=coin_id,
                    headers=config["headers"],
                    parse=config["sources"],
                    miss_markets=(
                        (coin_url in miss_markets)
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

            except ServerTimeoutError:
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

        save_coin(coin, config_url)
