from typing import Any
from get_coin import get_coin_from_db


def replace_macroses(var: str, coin):
    for key in coin.keys():
        coin[key] = str(coin[key])

    var = var.replace("coin", f"'{coin['name']}'")
    var = var.replace("ticker", f"'{coin['ticker']}'")
    var = var.replace("price", coin["price"])
    var = var.replace("24h_volume", coin["volume_24h"])
    var = var.replace("market_cap", coin["market_cap"])
    var = var.replace("add_to_portfolio", coin["portfolio"])
    var = var.replace("chains", str(len(coin["chains"].split(","))))
    var = var.replace("all_time_high", coin["ath"])
    var = var.replace("date_all_time_high", f"'{coin['ath_date']}'")
    var = var.replace("all_time_low", coin["atl"])
    var = var.replace("date_all_time_low", f"'{coin['atl_date']}'")
    var = var.replace("dex", coin["market_dex"])
    var = var.replace("cex", coin["market_cex"])
    var = var.replace("twitter_subscriber", coin["twitter_subs"])
    var = var.replace("twitter_posts", coin["twitter_posts"])
    var = var.replace("telegram_chanel_subscriber", coin["telegram_channel_subs"])
    var = var.replace("telegram_group_subscriber", coin["telegram_group_subs"])
    var = var.replace("telegram_group_online", coin["telegram_group_online"])
    var = var.replace("discord_subscriber", coin["discord_subs"])
    var = var.replace("discord_online", coin["discord_online"])
    var = var.replace("facebook_subscriber", coin["facebook_subs"])
    var = var.replace("facebook_like", coin["facebook_like"])
    var = var.replace("github_followers", coin["github_followers"])
    var = var.replace("github_projects", coin["github_projects"])
    var = var.replace("github_people", coin["github_people"])
    var = var.replace("github_repositories", coin["github_repositories"])
    var = var.replace(
        "github_repositories_last_date", f"'{coin['github_repositories_last_date']}'"
    )
    var = var.replace("parsing_date", f"'{coin['parsing_date']}'")
    var = var.replace("changes1h", coin['price_1h'])
    var = var.replace("changes24h", coin['price_24h'])
    var = var.replace("changes7d", coin['price_7d'])

    return var


def parse_macroses(var: str, coin_id: str, config_url):
    is_formula = False
    curr_formula = ""
    formula_end = 0

    for c in range(len(var) - 1, -1, -1):
        if var[c] == "}":
            is_formula = True
            formula_end = c
            continue

        if var[c] == "{":
            is_formula = False

            timestamp = int(curr_formula.split("_")[-1].split("h")[0])
            macros = "_".join(curr_formula.split("_")[0:-1])
            coin = get_coin_from_db(
                coin_id=coin_id, config_url=config_url, timestamp=timestamp
            )

            var = var[0:c] + replace_macroses(macros, coin) + var[formula_end + 1 :]
            curr_formula = ""

        if is_formula:
            curr_formula = var[c] + curr_formula

    return var


if __name__ == "__main__":
    print(parse_macroses("{price_0h} - {github_followers_0h}", "maple", "module-1.ini"))
