import json
import os

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from secret import TOKEN
from answers import START_BUTTON
from handlers.user_init import collect_init_from_user
from back.to_another_site import get_kkal

dp = Dispatcher()


users = {}  # авторизованные пользователи с информацией
if os.path.exists("save_users.txt"):
    with open("save_users.txt", "r") as file:
        users_str = file.read()
        users = json.loads(users_str)
        print("users успешно прочитан из save_users:")
        print(users)
else:
    print("Файл save_users.txt не существует, создан пустой словарь users")
init_users = {}  # в процессе авторизации


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(START_BUTTON)


@dp.message()
async def receive_answer(message: Message) -> None:
    global users, init_users
    init_user = await collect_init_from_user(users, init_users, message)
    if init_user:
        answer = message.text
        print(f"Message: {answer}")
        product = await get_kkal(answer)
        print(f"From back site: {product}")
        if product:
            await message.answer(
                f"""Продукт: {product["title"]}
Ккалорий: {product["value"]}"""
            )

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
