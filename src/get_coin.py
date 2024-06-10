import configparser
import time
import aiohttp
from aiohttp.web_exceptions import HTTPUseProxy, HTTPMovedPermanently
from aiohttp.client_exceptions import ClientProxyConnectionError, ClientHttpProxyError, InvalidURL
import arrow
from bs4 import BeautifulSoup
from colorama import Fore, Style
import asyncio
from check_db import check_db
from get_proxy import Proxy

import psycopg2
import psycopg2.extras


def generate_null_coin(coin_id, url, parsing_date, cause="Not Found"):
    return {
        "name": coin_id,
        "number": 99999,
        "ticker": cause,
        "price": 0,
        "price_1h": 0,
        "price_24h": 0,
        "price_7d": 0,
        "volume_24h": 0,
        "market_cap": 0,
        "portfolio": 0,
        "categories": cause,
        "chains": cause,
        "ath": 0,
        "atl": 0,
        "ath_date": cause,
        "atl_date": cause,
        "market_dex": 0,
        "market_cex": 0,
        "url": url,
        "parsing_date": parsing_date,
        "twitter_subs": 0,
        "twitter_posts": 0,
        "telegram_channel_subs": 0,
        "telegram_group_subs": 0,
        "telegram_group_online": 0,
        "discord_subs": 0,
        "discord_online": 0,
        "facebook_subs": 0,
        "facebook_like": 0,
        "github_followers": 0,
        "github_projects": 0,
        "github_people": 0,
        "github_repositories": 0,
        "github_repositories_last_date": cause,
    }


async def get_coin(coin_id: str, headers, parse, miss_markets=False, proxy=None):
    coin_id = coin_id.strip().replace(" ", "-")
    url = "https://www.coingecko.com/en/coins/{0}".format(coin_id)

    print(
        "Parsing {0} page... ".format(
            coin_id
        ),
        end="",
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url, headers=headers, proxy=proxy, timeout=15
        ) as response:
            content = await response.text()

        parsing_date = arrow.utcnow().to("Europe/Moscow").format("YYYY-MM-DD-HH-mm-ss")

        coin = {}
        html = BeautifulSoup(content, "html.parser")

        if html.find(class_="gecko-font-desktop"):
            print(Fore.RED + "\nRATE LIMITED! 120 seconds sleep!\n" + Style.RESET_ALL)
            time.sleep(120)
            return await get_coin(coin_id, headers, parse, miss_markets, proxy)

        try:
            if (
                html.find(
                    class_="tw-font-bold tw-text-gray-900 dark:tw-text-moon-50 tw-text-3xl md:tw-text-4xl tw-leading-10"
                )
                .get_text()
                .strip()
                == "Preview Only"
            ):
                return generate_null_coin(coin_id, url, parsing_date, "Preview Only!")
        except:
            print(Fore.RED + "\nNot Found! " + url + "\n" + Style.RESET_ALL)
            return generate_null_coin(coin_id, url, parsing_date, "Not Found")

        try:
            coin["name"] = (
                html.find(
                    "div",
                    class_="tw-font-bold tw-text-gray-900 dark:tw-text-moon-50 tw-text-lg tw-leading-7 !tw-text-base 2lg:!tw-text-lg",
                )
                .get_text()
                .strip()
            )
        except:
            print(Fore.RED + "\nNot Found! " + url + "\n" + Style.RESET_ALL)
            return generate_null_coin(coin_id, url, parsing_date, "Not Found")

        coin["ticker"] = (
            html.find(
                "span",
                class_="tw-font-normal tw-text-gray-500 dark:tw-text-moon-200 tw-text-sm tw-leading-5 tw-mt-0.5",
            )
            .get_text()
            .strip()
            .split(" ")[0]
        )

        try:
            price_percentages_elems = html.find(
                "tbody",
                class_="tw-divide-y tw-divide-gray-200 tw-min-w-full dark:tw-divide-moon-700",
            ).find_all(
                class_="tw-text-gray-900 dark:tw-text-moon-50 tw-px-1 tw-py-2.5 2lg:tw-p-2.5 tw-bg-inherit tw-text-center"
            )

            price_percentages = []

            for i in range(3):
                price_elem = price_percentages_elems[i]

                if price_elem.find(class_="gecko-down"):
                    price_percentages.append(
                        -float(price_elem.get_text().strip().split("%")[0])
                    )
                elif price_elem.find(class_="gecko-up"):
                    price_percentages.append(
                        float(price_elem.get_text().strip().split("%")[0])
                    )

            coin["price_1h"] = (
                None if price_percentages[0] == "-" else price_percentages[0]
            )
            coin["price_24h"] = (
                None if price_percentages[1] == "-" else price_percentages[1]
            )
            coin["price_7d"] = (
                None if price_percentages[2] == "-" else price_percentages[2]
            )
        except:
            coin["price_1h"] = 0
            coin["price_24h"] = 0
            coin["price_7d"] = 0

        try:
            coin["number"] = (
                html.find(
                    "span",
                    class_="tw-inline-flex tw-items-center tw-rounded-md tw-bg-gray-100 dark:tw-bg-moon-400/20 tw-px-1.5 tw-py-0.5 tw-mt-0.5 tw-mr-3 2lg:tw-mr-0",
                )
                .get_text()
                .strip()
                .split("#")[1]
            )
        except:
            coin["number"] = "99999"
            print(Fore.YELLOW + "has no number. " + Style.RESET_ALL, end="")

        try:
            price_elem = html.find(
                "div",
                class_="tw-font-bold tw-text-gray-900 dark:tw-text-moon-50 tw-text-3xl md:tw-text-4xl tw-leading-10",
            )

            coin["price"] = (
                price_elem.find("span")
                .get_text()
                .strip()
                .split("$")[1]
                .replace(",", "")
            )
        except:
            coin["price"] = 0

        try:
            sub_data = html.find(
                class_="tw-grid tw-grid-cols-1 tw-divide-y tw-divide-gray-200 dark:tw-divide-moon-700"
            ).find_all(class_="tw-flex tw-justify-between tw-py-3")

            for row in sub_data:
                row_info = row.find(
                    class_="tw-text-gray-500 dark:tw-text-moon-200 tw-font-medium tw-text-sm tw-leading-5 tw-text-left"
                )

                if row_info is None:
                    continue

                info = (
                    list(
                        row.find(
                            class_="tw-text-gray-500 dark:tw-text-moon-200 tw-font-medium tw-text-sm tw-leading-5 tw-text-left"
                        ).children
                    )[0]
                    .get_text()
                    .strip()
                )
                if info == "Market Cap":
                    try:
                        coin["market_cap"] = "".join(
                            row.find(
                                class_="tw-text-gray-900 dark:tw-text-moon-50 tw-font-semibold tw-text-sm tw-leading-5 tw-pl-2 tw-text-right"
                            )
                            .get_text()
                            .strip()
                            .split("$")[1]
                            .split(",")
                        )
                    except:
                        coin["market_cap"] = 0
                if info == "24 Hour Trading Vol":
                    try:
                        coin["volume_24h"] = (
                            row.find(
                                class_="tw-text-gray-900 dark:tw-text-moon-50 tw-font-semibold tw-text-sm tw-leading-5 tw-pl-2 tw-text-right"
                            )
                            .get_text()
                            .strip()
                            .split("$")[1]
                            .replace(",", "")
                        )
                    except:
                        coin["volume_24h"] = 0
                    break
        except:
            coin["market_cap"] = 0
            coin["volume_24h"] = 0

        coin["portfolio"] = "".join(
            html.select_one("span.tw-font-regular:nth-child(2)")
            .get_text()
            .strip()
            .split(" ")[0]
            .split(",")
        )
        secondaty_rows = html.find(
            "div",
            class_="tw-relative 2lg:tw-mb-6 tw-grid tw-grid-cols-1 tw-divide-y tw-divide-gray-200 dark:tw-divide-moon-700",
        )
        secondaty_rows = secondaty_rows.findChildren("div", recursive=False)

        coin["categories"] = ""
        coin["chains"] = ""
        for row in secondaty_rows:
            try:
                try:
                    row = row.findChildren("div", recursive=False)[0].findChildren(
                        "div", recursive=False
                    )
                except IndexError:
                    continue

                row_title = row[0].get_text().strip()
                row_content = row[1]

                if row_title == "Community":
                    social_networks = row_content.find(
                        "div",
                        class_="tw-flex tw-items-center tw-gap-1 tw-flex-wrap tw-justify-end",
                    ).find_all("a")
                    for net in social_networks:
                        net_title = net.get_text().strip()
                        net_href = net.get("href")

                        if net_title == "Twitter":
                            if parse["twitter_pars"] == "on":
                                pass
                                # coin["twitter_subs"] =
                                # coin["twitter_posts"] =
                        if net_title == "Telegram":
                            if parse["telegram_pars"] == "on":
                                try:
                                    telegram_page = await session.get(
                                        net_href, headers=headers
                                    )
                                    soup = BeautifulSoup(
                                        await telegram_page.text(), "html.parser"
                                    )
                                    try:
                                        text = (
                                            soup.find(class_="tgme_page_extra")
                                            .get_text()
                                            .strip()
                                        )

                                        if "subscribers" in text:
                                            subs = int(text.split("subscribers")[0].replace(" ", ""))
                                            coin["telegram_channel_subs"] = subs
                                            coin["telegram_group_subs"] = 0
                                            coin["telegram_group_online"] = 0
                                        elif "member" in text:
                                            subs = int(text.split("member")[0].replace(" ", ""))
                                            coin["telegram_channel_subs"] = 0
                                            coin["telegram_group_subs"] = subs

                                            splited = text.split(",")

                                            if len(splited) == 2:
                                                coin["telegram_group_online"] = int(
                                                    splited[1].split("online")[0].replace(" ", "")
                                                )
                                    except AttributeError:
                                        coin["telegram_channel_subs"] = 0
                                        coin["telegram_group_subs"] = 0
                                        coin["telegram_group_online"] = 0
                                except InvalidURL:
                                    coin["telegram_channel_subs"] = 0
                                    coin["telegram_group_subs"] = 0
                                    coin["telegram_group_online"] = 0

                        if net_title == "Discord":
                            if parse["discord_pars"] == "on":
                                discord_soc = net_href.split("/")[-1]
                                discord_req = await session.get(
                                    f"https://discord.com/api/v9/invites/{discord_soc}?with_counts=true&with_expiration=true"
                                )
                                discord_req = await discord_req.json()

                                if "approximate_member_count" in discord_req:
                                    coin["discord_subs"] = discord_req[
                                        "approximate_member_count"
                                    ]
                                    coin["discord_online"] = discord_req[
                                        "approximate_presence_count"
                                    ]
                        if net_title == "Facebook":
                            if parse["facebook_pars"] == "on":
                                pass
                                # coin["facebook_subs"] =
                                # coin["facebook_like"] =

                if row_title == "Source Code":
                    coin_github = row_content.find("a").get("href").split("/")[-1]
                    if parse["github_pars"] == "on":
                        github_headers = dict(
                            {
                                "Accept": "application/vnd.github+json",
                                "X-GitHub-Api-Version": "2022-11-28",
                                "Authorization": "Bearer {0}".format(
                                    parse["github_token"]
                                ),
                            }
                        )
                        github_people = await session.get(
                            f"https://api.github.com/orgs/{coin_github}/members",
                            headers=github_headers,
                        )
                        github_org = await session.get(
                            f"https://api.github.com/orgs/{coin_github}",
                            headers=github_headers,
                        )
                        github_proj = await session.get(
                            f"https://api.github.com/orgs/{coin_github}/repos",
                            headers=github_headers,
                        )
                        github_people = await github_people.json()
                        github_org = await github_org.json()
                        github_proj = await github_proj.json()

                        if "followers" in github_org:
                            coin["github_followers"] = github_org["followers"]
                            coin["github_projects"] = len(github_proj)
                            coin["github_people"] = len(github_people)
                            coin["github_repositories"] = github_org["public_repos"]
                            coin["github_repositories_last_date"] = github_org["updated_at"]

                if row_title == "Chains":
                    first_chain = (
                        row_content.find(
                            "div",
                            class_="tw-max-w-[200px] tw-overflow-hidden tw-overflow-ellipsis",
                        )
                        .get_text()
                        .strip()
                    )
                    more_chains = list(
                        map(
                            lambda x: x.get_text().strip(),
                            row_content.find_all(
                                "a",
                                class_="dark:tw-text-moon-100 dark:hover:tw-bg-moon-700 dark:hover:tw-text-moon-50 hover:tw-bg-gray-100 hover:tw-text-gray-900 tw-flex tw-items-center tw-py-3 tw-px-2 tw-rounded-lg tw-font-semibold tw-text-gray-700 tw-text-sm",
                            ),
                        )
                    )

                    coin["chains"] = ", ".join([first_chain, *more_chains])

                coin["twitter_subs"] = (
                    0 if "twitter_subs" not in coin else coin["twitter_subs"]
                )
                coin["twitter_posts"] = (
                    0 if "twitter_posts" not in coin else coin["twitter_posts"]
                )
                coin["telegram_channel_subs"] = (
                    0
                    if "telegram_channel_subs" not in coin
                    else coin["telegram_channel_subs"]
                )
                coin["telegram_group_subs"] = (
                    0
                    if "telegram_group_subs" not in coin
                    else coin["telegram_group_subs"]
                )
                coin["telegram_group_online"] = (
                    0
                    if "telegram_group_online" not in coin
                    else coin["telegram_group_online"]
                )
                coin["discord_subs"] = (
                    0 if "discord_subs" not in coin else coin["discord_subs"]
                )
                coin["discord_online"] = (
                    0 if "discord_online" not in coin else coin["discord_online"]
                )
                coin["facebook_subs"] = (
                    0 if "facebook_subs" not in coin else coin["facebook_subs"]
                )
                coin["facebook_like"] = (
                    0 if "facebook_like" not in coin else coin["facebook_like"]
                )
                coin["github_followers"] = (
                    0 if "github_followers" not in coin else coin["github_followers"]
                )
                coin["github_projects"] = (
                    0 if "github_projects" not in coin else coin["github_projects"]
                )
                coin["github_people"] = (
                    0 if "github_people" not in coin else coin["github_people"]
                )
                coin["github_repositories"] = (
                    0
                    if "github_repositories" not in coin
                    else coin["github_repositories"]
                )
                coin["github_repositories_last_date"] = (
                    ""
                    if "github_repositories_last_date" not in coin
                    else coin["github_repositories_last_date"]
                )

                if row_title == "Categories":
                    first_category = (
                        row_content.find(
                            "div",
                            class_="tw-max-w-[200px] tw-overflow-hidden tw-overflow-ellipsis",
                        )
                        .get_text()
                        .strip()
                    )
                    more_categories = list(
                        map(
                            lambda x: x.get_text().strip(),
                            row_content.find_all(
                                "a",
                                class_="dark:tw-text-moon-100 dark:hover:tw-bg-moon-700 dark:hover:tw-text-moon-50 hover:tw-bg-gray-100 hover:tw-text-gray-900 tw-flex tw-items-center tw-py-3 tw-px-2 tw-rounded-lg tw-font-semibold tw-text-gray-700 tw-text-sm",
                            ),
                        )
                    )

                    coin["categories"] = ", ".join([first_category, *more_categories])
                    break
            except Exception as e:
                print(e)
                print(Fore.YELLOW + "has no categories. " + Style.RESET_ALL, end="")
                continue

        try:
            tertiary_rows = (
                html.find(class_="2lg:tw-order-2")
                .find(
                    "tbody",
                    class_="tw-grid tw-grid-cols-1 tw-divide-y tw-divide-gray-200 dark:tw-divide-moon-700",
                )
                .find_all("tr")
            )

            for row in tertiary_rows:
                row_title = row.find("th").get_text().strip()

                if row_title == "All-Time High":
                    data = row.find("td").findChildren("div", recusive=False)
                    ath_elem = data[0].findChildren("span", recusive=False)[0]

                    if ath_elem.find("sub"):
                        coin["ath"] = ath_elem.find("sub").get("title")
                    else:
                        coin["ath"] = (
                            ath_elem.get_text().strip().split("$")[1].replace(",", "")
                        )

                    coin["ath_date"] = arrow.get(
                        " ".join(data[1].get_text().strip().split(" ")[0:3]),
                        "MMM DD, YYYY",
                    ).format("DD.MM.YYYY")
                if row_title == "All-Time Low":
                    data = row.find("td").findChildren("div", recusive=False)
                    atl_elem = data[0].findChildren("span", recusive=False)[0]

                    if ath_elem.find("sub"):
                        coin["atl"] = atl_elem.find("sub").get("title")
                    else:
                        coin["atl"] = (
                            atl_elem.get_text().strip().split("$")[1].replace(",", "")
                        )
                    coin["atl_date"] = arrow.get(
                        " ".join(data[1].get_text().strip().split(" ")[0:3]),
                        "MMM DD, YYYY",
                    ).format("DD.MM.YYYY")
                    break
        except:
            coin["ath"] = 0
            coin["atl"] = 0
            coin["ath_date"] = "-"
            coin["atl_date"] = "-"

        coin["url"] = url

        markets_url = f"https://www.coingecko.com/en/coins/{coin_id}/markets/spot"
        markets_req = await session.get(markets_url, headers=headers, proxy=proxy)
        markets_html = BeautifulSoup(await markets_req.text(), "html.parser")

        markets = {"DEX": {}, "CEX": {}}

        if not miss_markets:
            try:
                market_count = markets_html.find(
                    class_="tw-text-xs tw-leading-4 tw-text-gray-500 dark:tw-text-moon-200 tw-font-regular tw-hidden sm:tw-inline-flex gecko-pagination-results",
                )

                if not market_count:
                    market_count = markets_html.find(
                        class_="tw-text-xs tw-leading-4 tw-text-gray-500 dark:tw-text-moon-200 tw-font-regular tw-hidden sm:tw-inline-flex",
                    )

                market_count = int(market_count.get_text().strip().split(" ")[5])
                page_count = market_count // 100

                print(f"Markets count: {market_count}. Parsing markets...")
                for i in range(1, page_count + 2):
                    page_url = f"https://www.coingecko.com/en/coins/{coin_id}/markets/spot?items=100&page={i}"
                    page_req = await session.get(page_url, headers=headers, proxy=proxy)
                    page_html = BeautifulSoup(await page_req.text(), "html.parser")

                    market_rows = page_html.find_all(
                        "tr",
                        class_="hover:tw-bg-gray-50 tw-bg-white dark:tw-bg-moon-900 hover:dark:tw-bg-moon-800 tw-text-sm",
                    )

                    for row in market_rows:
                        market_title = (
                            row.find(
                                "div",
                                class_="tw-text-gray-700 dark:tw-text-moon-100 tw-font-semibold tw-text-sm tw-leading-5",
                            )
                            .get_text()
                            .strip()
                        )
                        mode = (
                            row.find(
                                "div",
                                class_="tw-text-xs tw-leading-4 tw-text-gray-700 dark:tw-text-moon-200 tw-font-medium",
                            )
                            .get_text()
                            .strip()
                        )
                        markets[mode][market_title] = 1
            except:
                print(Fore.YELLOW + "has no markets... " + Style.RESET_ALL, end="")
        else:
            print(Fore.RED + "Missing parsing markets" + Style.RESET_ALL)

        coin["market_cex"] = len(markets["CEX"].keys())
        coin["market_dex"] = len(markets["DEX"].keys())

        coin["parsing_date"] = parsing_date

        return coin


def get_coin_from_db(
    coin_id: str, config_url: str, timestamp: int = 0, partial: bool = False
):
    config = configparser.ConfigParser()
    config.read(config_url)

    db_table = (
        config["DB"]["db_table"] if not partial else config["DB"]["db_partial_table"]
    )

    check_db(config["DB"])

    conn = psycopg2.connect(
        database=config["DB"]["database"],
        host=config["DB"]["host"],
        port=config["DB"]["port"],
        user=config["DB"]["user"],
        password=config["DB"]["password"],
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute(
        f"SELECT * FROM {db_table} WHERE url = 'https://www.coingecko.com/en/coins/{coin_id}' and TO_TIMESTAMP(parsing_date, 'YYYY-MM-DD-HH24-MI-SS') <= NOW() - INTERVAL '{timestamp} hour' ORDER BY parsing_date DESC LIMIT 1;"
    )
    coin = dict(cursor.fetchone())

    cursor.close()
    conn.close()

    return coin


async def main():
    config = configparser.ConfigParser()
    config.read("module-1.ini")

    coin = get_coin_from_db(
        "cosmos-hub",
        config_url="module-2.ini"
    )

    print(coin)


if __name__ == "__main__":
    asyncio.run(main())
    # print(get_coin_from_db("maple", "module-1.ini"))
