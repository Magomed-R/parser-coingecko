import asyncio
from colorama import Fore, Style
from aiogram.types import FSInputFile


from aiogram.exceptions import TelegramRetryAfter


async def send_post(bot, text, channel, diagram_path):
    try:
        await bot.send_photo(
            chat_id=channel,
            photo=FSInputFile(diagram_path),
            caption=text,
        )
    except TelegramRetryAfter as error:
        print(
            Fore.RED
            + f"Flood error. Sleep {error.retry_after} seconds"
            + Style.RESET_ALL
        )
        await asyncio.sleep(error.retry_after)
        print(Fore.GREEN + "posting continued..." + Style.RESET_ALL)

        await bot.send_photo(
            chat_id=channel,
            photo=FSInputFile(diagram_path),
            caption=text,
        )
