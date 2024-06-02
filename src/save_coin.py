import configparser
import psycopg2
import psycopg2.extras

from check_db import check_db


def save_coin(coin, config_url, partial: bool = False):
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

    check_db(config["DB"], partial=partial)

    db_table = config["DB"]["db_partial_table"] if partial else config["DB"]["db_table"]

    cursor.execute(
        """ 
        INSERT INTO {0} (
                    name,
                    number,
                    ticker,
                    price,
                    price_1h,
                    price_24h,
                    price_7d,
                    market_cap,
                    volume_24h,
                    portfolio,
                    chains,
                    categories,
                    ath,
                    ath_date,
                    atl,
                    atl_date,
                    url,
                    market_cex,
                    market_dex,
                    parsing_date,
                    twitter_subs,
                    twitter_posts,
                    telegram_channel_subs,
                    telegram_group_subs,
                    telegram_group_online,
                    discord_subs,
                    discord_online,
                    facebook_subs,
                    facebook_like,
                    github_followers,
                    github_projects,
                    github_people,
                    github_repositories,
                    github_repositories_last_date
        ) VALUES (
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s, 
                    %s
        );
    """.format(db_table),
        (
            coin["name"],
            coin["number"],
            coin["ticker"],
            coin["price"],
            coin["price_1h"],
            coin["price_24h"],
            coin["price_7d"],
            coin["market_cap"],
            coin["volume_24h"],
            coin["portfolio"],
            coin["chains"],
            coin["categories"],
            coin["ath"],
            coin["ath_date"],
            coin["atl"],
            coin["atl_date"],
            coin["url"],
            coin["market_cex"],
            coin["market_dex"],
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
        ),
    )
    conn.commit()

    cursor.close()
    conn.close()
