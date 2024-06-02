from configparser import ConfigParser
import json
from aiogram import Bot

from create_diagram import create_diagram
from get_formulas import get_formulas
from parse_diagram import parse_diagram
from parse_text import parse_text
from send_post import send_post


"""
? Постинг по расписанию:
* Получение шаблона текста -> 
* Получение формул -> 
* Расчёт формул -> 
* Подставление формул под конкретную монету -> 
* Парсинг диаграммы -> 
* Отправка сообщения
"""


async def scheduled_posting(bot: Bot, config_url: str):
    config = ConfigParser()
    config.read(config_url)

    if config["default"]["should_parse"] != "on":
        return None

    print("scheduled posting...")

    with open(config["default"]["parsing_coins"]) as f:
        coins_urls_list = f.read().split("\n")

    with open(config["message"]["text"]) as f:
        main_text = f.read()

    text = (
        f"{main_text}\n\n<a href='{config['message']['footer_url']}'>{config['message']['footer']}</a>"
    )

    for coin_url in coins_urls_list:
        coin_id = coin_url.split("/")[-1]

        formulas = get_formulas(coin_id=coin_id, config_file_path=config_url)
        diagram_val = parse_diagram(config["message"]["diagram"], formulas)

        create_diagram(diagram_val, config["default"]["out_table"])

        message_text = parse_text(text, formulas)

        for channel in json.loads(config["default"]["channels"]):
            await send_post(bot, message_text, channel, config["default"]["out_table"])