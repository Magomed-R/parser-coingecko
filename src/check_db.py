import psycopg2
import psycopg2.extras


def check_db(config: dict["str", "str"], partial: bool = False):
    conn = psycopg2.connect(
        database=config["database"],
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    db_table = config["db_partial_table"] if partial else config["db_table"]

    cursor.execute(""" 
        create table if not exists {0} (
            name varchar(255),
            number int, 
            ticker varchar(255), 
            price double precision, 
            price_1h double precision,
            price_24h double precision,
            price_7d double precision,
            volume_24h NUMERIC(19, 4),
            market_cap NUMERIC(19, 4),
            portfolio int,
            categories text DEFAULT '',
            chains text DEFAULT '',
            ath double precision,
            atl double precision,
            ath_date varchar(255),
            atl_date varchar(255),
            market_dex int DEFAULT 0,
            market_cex int DEFAULT 0,
            url text,
            parsing_date varchar(255) DEFAULT CURRENT_TIMESTAMP,
            twitter_subs int DEFAULT 0,
            twitter_posts int DEFAULT 0,
            telegram_channel_subs int DEFAULT 0,
            telegram_group_subs int DEFAULT 0,
            telegram_group_online int DEFAULT 0,
            discord_subs int DEFAULT 0,
            discord_online int DEFAULT 0,
            facebook_subs int DEFAULT 0,
            facebook_like int DEFAULT 0,
            gitHub_followers int DEFAULT 0,
            gitHub_projects int DEFAULT 0,
            gitHub_people int DEFAULT 0,
            gitHub_repositories int DEFAULT 0,
            gitHub_repositories_last_date varchar(255) DEFAULT ''
        );
    """.format(db_table))
    conn.commit()
