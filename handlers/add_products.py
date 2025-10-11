from datetime import datetime

from aiogram.types import CallbackQuery


async def add_product(
    db,
    temporary_products: dict,
    notification: dict,
    callback: CallbackQuery,
):
    user_id = callback.from_user.id
    current_datetime = datetime.now()
    time_string = current_datetime.strftime("%d-%m-%Y")
    product_name = temporary_products[user_id]["name"]
    calories_product = temporary_products[user_id]["calories"]
    db.add_product(user_id, time_string, product_name, calories_product)
    del temporary_products[user_id]

    max_calories = db.get_user_info(user_id)["calories"]
    itogo_calories = db.get_total_calories_by_date(user_id, time_string)
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
