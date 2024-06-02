import configparser
import pandas
import psycopg2
import psycopg2.extras

from check_db import check_db


def export(config_url):
    config = configparser.ConfigParser()
    config.read(config_url)

    conn = psycopg2.connect(
        database=config["DB"]["database"],
        host=config["DB"]["host"],
        port=config["DB"]["port"],
        user=config["DB"]["user"],
        password=config["DB"]["password"],
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("select * from {0};".format(config["DB"]["db_table"]))
    coins = cursor.fetchall()

    output_data = pandas.DataFrame(
        columns=[
            "Number",
            "Coin",
            "Ticker",
            "Price",
            "1h",
            "24h",
            "7d",
            "24h Volume",
            "Market Cap",
            "Add to Portfolio",
            "Chains",
            "Categories",
            "All-Time High",
            "All-Time High Date",
            "All-Time Low",
            "All-Time Low Date",
            "Markets DEX",
            "Markets CEX",
            "URL coin",
            "Date pars",
            "Twitter subscriber",
            "Twitter posts",
            "Telegram chanel subscriber",
            "Telegram group subscriber",
            "Telegram group online",
            "Discord subscriber",
            "Discord online",
            "Facebook subscriber",
            "Facebook like",
            "GitHub followers",
            "GitHub projects",
            "GitHub people",
            "GitHub repositories",
            "GitHub repositories last date",
        ],
    )

    for i in range(len(coins)):
        coin = coins[i]
        output_data.loc[i] = [
            coin["number"],
            coin["name"],
            coin["ticker"],
            coin["price"],
            coin["price_1h"],
            coin["price_24h"],
            coin["price_7d"],
            coin["volume_24h"],
            coin["market_cap"],
            coin["portfolio"],
            coin["categories"],
            coin["chains"],
            coin["ath"],
            coin["atl"],
            coin["ath_date"],
            coin["atl_date"],
            coin["market_dex"],
            coin["market_cex"],
            coin["url"],
            coin["parsing_date"],
            coin["twitter_subs"],
            coin["twitter_posts"],
            coin["telegram_channel_subs"],
            coin["telegram_group_subs"],
            coin["telegram_group_online"],
            coin["discord_subs"],
            coin["discord_online"],
            coin["facebook_subs"],
            coin["facebook_like"],
            coin["github_followers"],
            coin["github_projects"],
            coin["github_people"],
            coin["github_repositories"],
            coin["github_repositories_last_date"],
        ]

    output_data.to_excel(config['default']['out_table'], sheet_name="coins")

    cursor.close()
    conn.close()


def export_24h(config_url):
    config = configparser.ConfigParser()
    config.read(config_url)

    conn = psycopg2.connect(
        database=config["DB"]["database"],
        host=config["DB"]["host"],
        port=config["DB"]["port"],
        user=config["DB"]["user"],
        password=config["DB"]["password"],
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("select * from {0} where TO_TIMESTAMP(parsing_date, 'YYYY-MM-DD-HH24-MI-SS') >= NOW() - INTERVAL '1 day';".format(config["DB"]["db_table"]))
    coins = cursor.fetchall()

    output_data = pandas.DataFrame(
        columns=[
            "Number",
            "Coin",
            "Ticker",
            "Price",
            "1h",
            "24h",
            "7d",
            "24h Volume",
            "Market Cap",
            "Add to Portfolio",
            "Chains",
            "Categories",
            "All-Time High",
            "All-Time High Date",
            "All-Time Low",
            "All-Time Low Date",
            "Markets DEX",
            "Markets CEX",
            "URL coin",
            "Date pars",
            "Twitter subscriber",
            "Twitter posts",
            "Telegram chanel subscriber",
            "Telegram group subscriber",
            "Telegram group online",
            "Discord subscriber",
            "Discord online",
            "Facebook subscriber",
            "Facebook like",
            "GitHub followers",
            "GitHub projects",
            "GitHub people",
            "GitHub repositories",
            "GitHub repositories last date",
        ],
    )

    for i in range(len(coins)):
        coin = coins[i]
        output_data.loc[i] = [
            coin["number"],
            coin["name"],
            coin["ticker"],
            coin["price"],
            coin["price_1h"],
            coin["price_24h"],
            coin["price_7d"],
            coin["volume_24h"],
            coin["market_cap"],
            coin["portfolio"],
            coin["categories"],
            coin["chains"],
            coin["ath"],
            coin["atl"],
            coin["ath_date"],
            coin["atl_date"],
            coin["market_dex"],
            coin["market_cex"],
            coin["url"],
            coin["parsing_date"],
            coin["twitter_subs"],
            coin["twitter_posts"],
            coin["telegram_channel_subs"],
            coin["telegram_group_subs"],
            coin["telegram_group_online"],
            coin["discord_subs"],
            coin["discord_online"],
            coin["facebook_subs"],
            coin["facebook_like"],
            coin["github_followers"],
            coin["github_projects"],
            coin["github_people"],
            coin["github_repositories"],
            coin["github_repositories_last_date"],
        ]

    output_data.to_excel(config['default']['out_table'], sheet_name="coins")

    cursor.close()
    conn.close()

def export_24h_partial(config_url):
    config = configparser.ConfigParser()
    config.read(config_url)

    conn = psycopg2.connect(
        database=config["DB"]["database"],
        host=config["DB"]["host"],
        port=config["DB"]["port"],
        user=config["DB"]["user"],
        password=config["DB"]["password"],
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("select * from {0} where TO_TIMESTAMP(parsing_date, 'YYYY-MM-DD-HH24-MI-SS') >= NOW() - INTERVAL '1 day';".format(config["DB"]["db_partial_table"]))
    coins = cursor.fetchall()

    output_data = pandas.DataFrame(
        columns=[
            "Number",
            "Coin",
            "Ticker",
            "Price",
            "1h",
            "24h",
            "7d",
            "24h Volume",
            "Market Cap",
            "Add to Portfolio",
            "Chains",
            "Categories",
            "All-Time High",
            "All-Time High Date",
            "All-Time Low",
            "All-Time Low Date",
            "Markets DEX",
            "Markets CEX",
            "URL coin",
            "Date pars",
            "Twitter subscriber",
            "Twitter posts",
            "Telegram chanel subscriber",
            "Telegram group subscriber",
            "Telegram group online",
            "Discord subscriber",
            "Discord online",
            "Facebook subscriber",
            "Facebook like",
            "GitHub followers",
            "GitHub projects",
            "GitHub people",
            "GitHub repositories",
            "GitHub repositories last date",
        ],
    )

    for i in range(len(coins)):
        coin = coins[i]
        output_data.loc[i] = [
            coin["number"],
            coin["name"],
            coin["ticker"],
            coin["price"],
            coin["price_1h"],
            coin["price_24h"],
            coin["price_7d"],
            coin["volume_24h"],
            coin["market_cap"],
            coin["portfolio"],
            coin["categories"],
            coin["chains"],
            coin["ath"],
            coin["atl"],
            coin["ath_date"],
            coin["atl_date"],
            coin["market_dex"],
            coin["market_cex"],
            coin["url"],
            coin["parsing_date"],
            coin["twitter_subs"],
            coin["twitter_posts"],
            coin["telegram_channel_subs"],
            coin["telegram_group_subs"],
            coin["telegram_group_online"],
            coin["discord_subs"],
            coin["discord_online"],
            coin["facebook_subs"],
            coin["facebook_like"],
            coin["github_followers"],
            coin["github_projects"],
            coin["github_people"],
            coin["github_repositories"],
            coin["github_repositories_last_date"],
        ]

    output_data.to_excel(config['default']['out_table'], sheet_name="coins")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("fullparser.ini")
    check_db(config["DB"])

    export_24h("fullparser.ini")
