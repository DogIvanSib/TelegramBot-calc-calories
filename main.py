import json
import os
from datetime import datetime

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from secret import TOKEN
from answers import START_BUTTON, ABOUT_BUTTON
from handlers.user_init import collect_init_from_user
from back.to_another_site import get_kkal
from keyboards.keyboard import get_keyboard
from handlers.add_products import add_product

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
temporary_products = {}  # временные продукты

products = {}  # продукты после нажатия на добавить
if os.path.exists("save_products.txt"):
    with open("save_products.txt", "r") as file:
        products_str = file.read()
        products = json.loads(products_str)
        products = {int(k): v for k, v in products.items()}
        print("products успешно прочитан из save_products:")
        print(products)
else:
    print("Файл save_products.txt не существует, создан пустой словарь products")

notification = {}  # одно предупреждение что скушал много


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
        await message.answer(
            "🎯 <b>Сначала нужно познакомиться!</b>\n\n"
            "📋 Для точных расчётов мне нужна информация о вас\n\n"
            "👉 Используйте команду: /sent_info\n\n"
            "<i>Это займёт всего 2 минуты</i> ⏱️",
        )


@dp.message(Command("stats_week"))
async def stats_handler(message: Message):
    """This handler receives messages with `/stats_week` command"""
    user_id = message.from_user.id
    if users.get(user_id, None):
        await message.answer("Функция в разработке.")
    else:
        await message.answer(
            "🎯 <b>Сначала нужно познакомиться!</b>\n\n"
            "📋 Для точных расчётов мне нужна информация о вас\n\n"
            "👉 Используйте команду: /sent_info\n\n"
            "<i>Это займёт всего 2 минуты</i> ⏱️",
        )


@dp.message(Command("stats_today"))
async def stats_handler(message: Message):
    """This handler receives messages with `/stats_today` command"""
    user_id = message.from_user.id
    if users.get(user_id, None):
        current_datetime = datetime.now()
        time_string = current_datetime.strftime("%d-%m-%Y")
        if products.get(user_id, None):
            calories = products[user_id].get(time_string, 0)
            await message.answer(
                f"🍽️ Съедено {time_string}: <b>{calories}</b> ккал\n"
                f"🎯 Норма: <b>{users[user_id]['calories']}</b> ккал"
            )
        else:
            await message.answer(
                f"🍽️ Съедено {time_string}: <b>0</b> ккал\n"
                f"🎯 Норма: <b>{users[user_id]['calories']}</b> ккал"
            )
    else:
        await message.answer(
            "🎯 <b>Сначала нужно познакомиться!</b>\n\n"
            "📋 Для точных расчётов мне нужна информация о вас\n\n"
            "👉 Используйте команду: /sent_info\n\n"
            "<i>Это займёт всего 2 минуты</i> ⏱️",
        )


@dp.message(Command("about"))
async def stats_handler(message: Message):
    """This handler receives messages with `/about` command"""
    await message.answer(ABOUT_BUTTON)


@dp.message()
async def receive_answer(message: Message) -> None:
    global users, init_users
    init_user = await collect_init_from_user(users, init_users, message)
    if init_user:
        answer = message.text
        user_id = message.from_user.id
        print(f"Message: {answer}")
        product = await get_kkal(answer)
        print(f"From back site: {product}")
        if product:
            temporary_products[user_id] = {
                "name": product["title"],
                "calories": int(product["value"]),
            }
            await message.answer(
                "📦 <b>Продукт:</b>\n"
                f"  📝 <b>Название:</b> {product['title']}\n"
                f"  💪 <b>Ккалории:</b> {product['value']}",
                reply_markup=get_keyboard(),
            )


@dp.callback_query(F.data.startswith("product_save"))
async def callbacks_product_save(callback: CallbackQuery):
    global products, users, temporary_products, notification
    user_id = callback.from_user.id
    name_product = temporary_products.get(user_id)["name"]
    calories_product = temporary_products.get(user_id)["calories"]
    if not name_product and calories_product:
        return
    print(f"{user_id} нажал сохранить: {name_product}:{calories_product}")
    await add_product(
        products, users, temporary_products, notification, callback
    )  # действие на добавление, будущее прогназирование
    await callback.message.delete()
    await callback.message.answer(
        f"✅ Успешно добавил <b>{name_product}</b>: {calories_product} Ккал"
    )
    await callback.answer()


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
