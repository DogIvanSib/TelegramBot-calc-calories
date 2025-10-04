import json
import os

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
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
        users = {int(k): v for k, v in users.items()}
        print("users успешно прочитан из save_users:")
        print(users)
else:
    print("Файл save_users.txt не существует, создан пустой словарь users")
init_users = {}  # в процессе авторизации


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command"""
    await message.answer(START_BUTTON)


@dp.message(Command("profile"))
async def profile_handler(message: Message):
    """This handler receives messages with `/profile` command"""
    user_id = message.from_user.id
    if users.get(user_id, None):
        await message.answer(
            f"<b>Ваши данные:</b>\n"
            f"  📅 <b>Возраст:</b> {users[user_id]['age']} лет\n"
            f"  ⚖️ <b>Вес:</b> {users[user_id]['weight']} кг\n"
            f"  📏 <b>Рост:</b> {users[user_id]['height']} см"
        )
    else:
        await message.answer("Сперва нужно узнать о вас больше информации /sent_info")


@dp.message(Command("stats"))
async def stats_handler(message: Message):
    """This handler receives messages with `/stats` command"""
    user_id = message.from_user.id
    if users.get(user_id, None):
        await message.answer("Функция в разработке.")
    else:
        await message.answer("Сперва нужно узнать о вас больше информации /sent_info")


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
                "📦 <b>Продукт:</b>\n"
                f"  📝 <b>Название:</b> {product['title']}\n"
                f"  💪 <b>Ккалории:</b> {product['value']}"
            )


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
