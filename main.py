from datetime import datetime

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from secret import TOKEN, GIGA_AI_CREDENTIALS
from answers import START_BUTTON, ABOUT_BUTTON
from handlers.user_init import collect_init_from_user
from back.to_another_site import get_kkal
from keyboards.keyboard import get_keyboard, get_keyboard_photo
from handlers.add_products import add_product
from back.database import Database
from back.ai import AI
from handlers.graph import graph_week
from handlers.photo import photo_processing

dp = Dispatcher()
db = Database()
ai = AI(GIGA_AI_CREDENTIALS)

init_users = {}  # в процессе авторизации
temporary_products = {}  # временные продукты
notification = {}  # одно предупреждение что скушал много


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command"""
    await message.answer(START_BUTTON)


@dp.message(Command("profile"))
async def profile_handler(message: Message):
    """This handler receives messages with `/profile` command"""
    user_id = message.from_user.id
    if users := db.get_user_info(user_id):
        await message.answer(
            f"<b>Ваши данные:</b>\n"
            f"  📅 <b>Возраст:</b> {users['age']} лет\n"
            f"  ⚖️ <b>Вес:</b> {users['weight']} кг\n"
            f"  📏 <b>Рост:</b> {users['height']} см\n"
            f"  ⚖️ <b>Норма Ккалорий:</b> {users['calories']}"
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
    if db.get_user_info(user_id):
        stat_week_kcal, itogo_week = db.get_weekly_calories(user_id)
        await graph_week(message, stat_week_kcal, itogo_week)
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
    if user := db.get_user_info(user_id):
        current_datetime = datetime.now()
        time_string = current_datetime.strftime("%d-%m-%Y")
        total_calories = db.get_total_calories_by_date(user_id, time_string)
        all_products_by_user = db.get_user_products_by_date(user_id, time_string)
        all_products_by_user_str = "\n".join(
            [
                f"     {p["product_name"]}: {int(p["calories"])}"
                for p in all_products_by_user
            ]
        )
        await message.answer(
            f"🍽️ Съедено {time_string}: <b>{total_calories}</b> ккал\n"
            f"🎯 Норма: <b>{user['calories']}</b> ккал\n\n"
            f"📝 ПОДРОБНЫЙ УЧЕТ:\n{all_products_by_user_str}"
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


@dp.message(Command("recommendations"))
async def stats_handler(message: Message):
    """This handler receives messages with `/recommendations` command"""
    user_id = message.from_user.id
    if user := db.get_user_info(user_id):
        like_menu = db.get_user_top_products_this_week(user_id)
        stat_week_kcal, _ = db.get_weekly_calories(user_id)
        await message.answer(await ai.menu_analysis(stat_week_kcal, like_menu, user))
    else:
        await message.answer(
            "🎯 <b>Сначала нужно познакомиться!</b>\n\n"
            "📋 Для точных расчётов мне нужна информация о вас\n\n"
            "👉 Используйте команду: /sent_info\n\n"
            "<i>Это займёт всего 2 минуты</i> ⏱️",
        )


@dp.message()
async def receive_answer(message: Message) -> None:
    global init_users
    init_user = await collect_init_from_user(db, init_users, message)
    if init_user:
        user_id = message.from_user.id
        if message.photo:
            product = await photo_processing(message, ai)
            print(f"Получил от фото==={product}")
        else:
            answer = message.text
            print(f"Message: {answer}")
            product = await get_kkal(answer)
            print(f"From back site: {product}")
            if not product:
                product = await ai.get_kcal(answer)
        if product:
            temporary_products[user_id] = {
                "name": product["title"],
                "calories": int(product["value"]),
            }
            if product.get("photo"):
                await message.answer(
                    "📦 <b>Продукт:</b>\n"
                    f"  📝 <b>Название:</b> {product['title']}\n"
                    f"  💪 <b>Ккалории:</b> {product['value']}\n",
                    reply_markup=get_keyboard_photo(),
                )
            else:
                await message.answer(
                    "📦 <b>Продукт:</b>\n"
                    f"  📝 <b>Название:</b> {product['title']}\n"
                    f"  💪 <b>Ккалории:</b> {product['value']} в 100 грамм\n"
                    f"  🍽️ Выберите порцию:",
                    reply_markup=get_keyboard(),
                )


@dp.callback_query(F.data.startswith("product_save_photo"))
async def product_save_photo(callback: CallbackQuery):
    user_id = callback.from_user.id
    name_product = temporary_products.get(user_id)["name"]
    calories_product = temporary_products.get(user_id)["calories"]
    await callbacks_product_save(user_id, name_product, calories_product, callback)


@dp.callback_query(F.data.startswith("product_save_small"))
async def product_save_small(callback: CallbackQuery):
    user_id = callback.from_user.id
    name_product = temporary_products.get(user_id)["name"]
    calories_product = temporary_products.get(user_id)["calories"]
    await callbacks_product_save(user_id, name_product, calories_product, callback)


@dp.callback_query(F.data.startswith("product_save_midle"))
async def product_save_midle(callback: CallbackQuery):
    user_id = callback.from_user.id
    name_product = temporary_products.get(user_id)["name"]
    calories_product = temporary_products.get(user_id)["calories"] * 2
    await callbacks_product_save(user_id, name_product, calories_product, callback)


@dp.callback_query(F.data.startswith("product_save_big"))
async def product_save_big(callback: CallbackQuery):
    user_id = callback.from_user.id
    name_product = temporary_products.get(user_id)["name"]
    calories_product = temporary_products.get(user_id)["calories"] * 3
    await callbacks_product_save(user_id, name_product, calories_product, callback)


async def callbacks_product_save(
    user_id, name_product, calories_product, callback: CallbackQuery
):
    global temporary_products, notification
    if not name_product and calories_product:
        return
    print(f"{user_id} нажал сохранить: {name_product}:{calories_product}")
    await add_product(
        db, temporary_products, notification, name_product, calories_product, callback
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
