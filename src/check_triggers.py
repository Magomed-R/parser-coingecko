from configparser import ConfigParser
import json

from aiogram import Bot

from create_diagram import create_diagram
from get_formulas import get_formulas
from parse_diagram import parse_diagram
from parse_text import parse_text
from send_post import send_post

"""
? Реагирование на триггеры:
* Получение шаблона текста -> 
* Получение формул -> 
* Расчёт формул -> 
* Получение монеты из БД ->
* Проверка триггеров -> 
* Расчёт диаграммы -> 
* Отправка сообщения
"""

async def check_triggers(bot: Bot, config_url):
    config = ConfigParser()
    config.read(config_url)

    if config["trigger"]["trigger"] != "on":
        return None

    print("Check triggers...")

    with open(config["default"]["parsing_coins"]) as f:
        coins_urls_list = f.read().split("\n")

    with open(config["message"]["trigger_text"]) as f:
        main_text = f.read()

    with open(config["trigger"]["trigger_file"]) as f:
        triggers = f.read().split("\n")

    text = (
        f"{main_text}\n\n<a href='{config['message']['footer_url']}'>{config['message']['footer']}</a>"
    )

    for coin_url in coins_urls_list:
        coin_id = coin_url.split("/")[-1]

        formulas = get_formulas(coin_id=coin_id, config_file_path=config_url)

        worth_reacting = False

        for trigger in triggers:
            if trigger and eval(parse_text(trigger, formulas)):
                worth_reacting = True
        
        if worth_reacting:
            diagram_val = parse_diagram(config["message"]["diagram"], formulas)

            create_diagram(diagram_val, config["default"]["trigger_diagram"])

            message_text = parse_text(text, formulas)

            for channel in json.loads(config["default"]["channels"]):
                await send_post(bot, message_text, channel, config["default"]["out_table"])