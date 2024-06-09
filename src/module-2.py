import asyncio
import configparser
import json

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Any, Awaitable, Callable, Dict

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, Update, BotCommand
from aiogram.types import FSInputFile

from check_db import check_db
from check_triggers import check_triggers
from export_excel import export_24h
from parse_coins import parse_coins
from scheduled_posting import scheduled_posting

dp = Dispatcher()


@dp.update.outer_middleware()
async def check_admins(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
):
    config.read(config_url)
    admins = json.loads(config["default"]["admins"])

    if event.event.from_user.id not in admins:
        return await event.event.answer(
            "⛔Вы не можете использовать бота, так как вы не являетесь админом"
        )

    return await handler(event, data)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    config.read(config_url)

    if (
        config["default"]["should_parse"] == "on"
        and config["trigger"]["trigger"] == "on"
    ):
        with open(config_url, "w") as configfile:
            config.write(configfile)

        return await message.answer("✅Бот уже запущен!")
    else:
        config.set("default", "should_parse", "on")
        config.set("trigger", "trigger", "on")

        with open(config_url, "w") as configfile:
            config.write(configfile)

        return await message.answer("✅Бот успешно запущен!")


@dp.message(Command("stop"))
async def stop(message: Message):
    config.read(config_url)

    if (
        config["default"]["should_parse"] != "on"
        and config["trigger"]["trigger"] != "on"
    ):
        with open(config_url, "w") as configfile:
            config.write(configfile)

        return await message.answer("❎Бот уже остановлен!")
    else:
        config.set("default", "should_parse", "off")
        config.set("trigger", "trigger", "off")

        with open(config_url, "w") as configfile:
            config.write(configfile)

        return await message.answer("❎Бот успешно остановлен!")


@dp.message(Command("restart"))
async def restart(message: Message):
    config.read(config_url)
    config.set("default", "should_parse", "on")
    config.set("trigger", "trigger", "on")

    with open(config_url, "w") as configfile:
        config.write(configfile)

    return await message.answer("✅Бот успешно перезапущен!")


@dp.message(Command("stat"))
async def stat(message: Message):
    config.read(config_url)
    cache = json.load(open("cache.json", "r"))

    text = f"📊Статус бота\n\nПарсинг по расписанию: {'Выключен' if config['default']['should_parse'] != 'on' else 'Включен'}\nРеагирование на триггеры: {'Выключено' if config['trigger']['trigger'] != 'on' else 'Включено'}\nВремя последней публикации: {cache[config_url]['last_scheduled_post']}\n\n📊Статус полного парсера\n\nСпарсено: {cache['last_coin']} / 13845\nПоследняя монета: {cache['coin_name']}\nID последней монеты: {cache['coin_id']}"

    return await message.answer(text)


@dp.message(Command("get_archive"))
async def get_archive(message: Message):
    config.read(config_url)

    check_db(config["DB"])

    export_24h(config_url)
    return await message.answer_document(FSInputFile(config["default"]["out_table"]))


async def main(bot):
    try:
        config.read(config_url)

        scheduler = AsyncIOScheduler({"apscheduler.job_defaults.max_instances": 4})
        await bot.set_my_commands(
            commands=[
                BotCommand(command="start", description="Запустить бота"),
                BotCommand(command="restart", description="Перезапустить бота"),
                BotCommand(command="stop", description="Остановить бота"),
                BotCommand(command="stat", description="Состояние бота"),
                BotCommand(command="get_archive", description="Скачать архив"),
            ]
        )

        with open("cache.json", "r") as f:
            cache = json.load(f)

        with open("cache.json", "w") as f:
            if config_url not in cache:
                cache[config_url] = {}

            cache[config_url]["trigger"] = "off"
            cache[config_url]["schelude_parsing"] = "off"
            json.dump(cache, f)

        await parse_coins(config_url)
        await check_triggers(bot, config_url)
        await scheduled_posting(bot, config_url)

        scheduler.add_job(parse_coins, "interval", seconds=3600, args=[config_url])
        scheduler.add_job(
            check_triggers, "interval", seconds=10800, args=[bot, config_url]
        )
        scheduler.add_job(
            scheduled_posting,
            "interval",
            seconds=int(config["default"]["pars_period"]),
            args=[bot, config_url],
        )

        scheduler.start()

        await dp.start_polling(bot)
    except (SystemExit, KeyboardInterrupt):
        await dp.stop_polling(bot)
        scheduler.shutdown()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config_url = "module-2.ini"

    config.read(config_url)

    bot = Bot(
        token=config["default"]["bot_token"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    asyncio.run(main(bot))
