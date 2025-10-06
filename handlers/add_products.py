import json
from collections import defaultdict
from datetime import datetime

from aiogram.types import CallbackQuery


async def add_product(
    products: dict,
    users: dict,
    temporary_products: dict,
    notification: dict,
    callback: CallbackQuery,
):
    """products = {565062409: defaultdict(<class 'int'>, {'06-10-2025': 1278})}"""
    user_id = callback.from_user.id
    current_datetime = datetime.now()
    time_string = current_datetime.strftime("%d-%m-%Y")
    calories_product = temporary_products[user_id]["calories"]
    if user_id not in products:
        products[user_id] = defaultdict(int)
    products[user_id][time_string] += calories_product
    with open("save_products.txt", "w") as file:
        products_str = json.dumps(products)
        file.write(products_str)
        print("save_products успешно сохранен")
    del temporary_products[user_id]

    max_calories = users[user_id]["calories"]
    itogo_calories = products[user_id][time_string]
    if itogo_calories > max_calories / 2:
        if not notification.get(user_id, None) == time_string:
            await callback.message.answer(
                f"📈 <b>Анализ питания</b>\n\n"
                "<b>Вы уже набрали половину дневной нормы!</b>\n"
                f"• ✅ Дневной лимит: <b>{max_calories}</b> Ккал\n"
                f"• 📊 Потреблено: <b>{itogo_calories}</b> Ккал\n\n"
                "🌱 <b>Рекомендации:</b>\n"
                "▫️ Уменьшите размер порций\n"
                "▫️ Выбирайте продукты с низкой калорийностью\n"
                "▫️ Пейте больше воды перед едой\n\n"
                "💪 Вы справитесь!",
            )
            notification[user_id] = time_string
    if itogo_calories > max_calories:
        await callback.message.answer(
            f"📊 <b>Лимит калорий превышен</b>\n\n"
            f"✅ Съедено: <b>{itogo_calories}</b> Ккал\n"
            f"🎯 Максимум: <b>{max_calories}</b> Ккал\n\n"
            "🛑 <b>РЕКОМЕНДУЕТСЯ:</b>\n"
            "• Прекратить приём пищи\n"
            "• Пить воду или травяной чай\n"
            "• Следующий приём — завтрак\n\n"
            "💪 Держитесь! Завтра новый день!",
        )
    print(products)
