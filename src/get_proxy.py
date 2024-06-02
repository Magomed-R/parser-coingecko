import asyncio
import json
import os
import aiohttp
from colorama import Fore, Style

class Proxy():
    def __init__(self, proxy_file_path: str):
        with open("./cache.json", "r") as cache:
            self.current_proxy = json.load(cache)["fresh_proxy"]
            self.proxy_file_path = proxy_file_path
    
    async def next_proxy(self, as_dict = False):
        with open(self.proxy_file_path, "r") as f:
            proxies = f.read().split("\n")

        self.current_proxy = (self.current_proxy + 1) % len(proxies)

        with open("./cache.json", "r") as f:
            cache = json.load(f)
        
        with open("./cache.json", "w") as f:
            cache["fresh_proxy"] = self.current_proxy
            json.dump(cache, f)
        
        return await self.get_proxy(as_dict)

    async def get_proxy(self, as_dict = False):
        with open(self.proxy_file_path, "r") as f:
            proxies = f.read().strip().split("\n")

        proxy = proxies[self.current_proxy].split(":")
        proxy_json = {
            "protocol": "socks5",
            "user": proxy[2],
            "password": proxy[3],
            "ip": proxy[0],
            "port": proxy[1]
        }
        
        if as_dict:
            return proxy_json
        else:
            return f"{proxy_json['protocol']}://{proxy_json['user']}:{proxy_json['password']}@{proxy_json['ip']}:{proxy_json['port']}"


async def main():
    proxy = Proxy(proxy_file_path="proxy.txt")
    print(await proxy.get_proxy())
    print(await proxy.get_proxy(as_dict=True))
    print(await proxy.next_proxy())

if __name__ == "__main__":
    asyncio.run(main())


#^ Legacy. Here using webshare.io API.
""" 
auth_token = os.getenv("webshare_token")

class Proxy():
    def __init__(self):
        with open("./cache.json", "r") as cache:
            self.current_proxy = json.load(cache)["fresh_proxy"]

    async def get_proxy(self, country = "US,ES,RU,FR,IT,NL", as_dict = False):
        print("getting proxy... ", end="")
        session = aiohttp.ClientSession()

        get_proxy_req = await session.get(
            f"https://proxy.webshare.io/api/v2/proxy/list?mode=direct&country_code__in={country}",
            headers={ "Authorization": f"Token {auth_token}" }
        )
        proxies = (await get_proxy_req.json())["results"]

        proxy_json = proxies[self.current_proxy]

        proxy = f'socks5://{proxy_json["username"]}:{proxy_json["password"]}@{proxy_json["proxy_address"]}:{proxy_json["port"]}'
        
        await session.close()

        print(Fore.GREEN + "proxy received!" + Style.RESET_ALL)

        if as_dict:
            return proxy_json

        return dict({"http": proxy})


    def next_proxy():
        with open("cache.json", 'r') as cache:
            cache = json.load(cache)

        if (cache["fresh_proxy"] == 10 - 1):
            cache["fresh_proxy"] = 0
        else:
            cache["fresh_proxy"] = int(cache["fresh_proxy"]) + 1

        with open("cache.json", "w") as f:
            json.dump(cache, f) """
