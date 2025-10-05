import json
from copy import deepcopy

from aiogram.types import Message


async def collect_init_from_user(
    users: dict, init_users: dict, message: Message
) -> bool:
    """Собираю инфу о пользователе
    Example user:
    {565062409: {'age': 1, 'weight': 2, 'height': 3, 'gender': 'м', 'calories': 2000}}
    """
    user_id = message.from_user.id
    answer = message.text
    if user_id in users:
        print(f"{user_id} авторизован")
        return True
    elif user_id not in init_users:
        await collect_init_Q1(message)
        init_users[user_id] = {"age": None}
    elif user_id in init_users and init_users[user_id].get("age", -1) is None:
        init_users[user_id]["age"] = int(answer)
        await collect_init_Q2(message)
        init_users[user_id] |= {"weight": None}
    elif user_id in init_users and init_users[user_id].get("weight", -1) is None:
        init_users[user_id]["weight"] = int(answer)
        await collect_init_Q3(message)
        init_users[user_id] |= {"height": None}
    elif user_id in init_users and init_users[user_id].get("height", -1) is None:
        init_users[user_id]["height"] = int(answer)
        await collect_init_Q4(message)
        init_users[user_id] |= {"gender": None}
    elif user_id in init_users and init_users[user_id].get("gender", -1) is None:
        if answer.lower() == "м" or answer.lower() == "ж":
            init_users[user_id]["gender"] = answer.lower()
        else:
            await message.answer("Прошу вводить м или ж")
            return False
        init_users[user_id] |= {"calories": calc_calories(init_users[user_id])}
        #  Сохраняю в users
        users[user_id] = deepcopy(init_users[user_id])
        del init_users[user_id]
        print(f"users=={users}")
        with open("save_users.txt", "w") as file:
            users_str = json.dumps(users)
            file.write(users_str)
            print("save_users успешно сохранен")
        await message.answer(
            "✨ <b>Спасибо за информацию!</b>\n\n"
            "🍴 Рекомендую попробовать <i>мидии в сливочном соусе</i> — нежнейшее блюдо!"
        )
    else:
        print(f"Непонятная штука пришла в init_user. Answer: {answer}")
    print(f"init_users=={init_users}")
    return False


async def collect_init_Q1(message: Message):
    await message.answer(
        "📊 <b>Для точного расчета калорий</b>\n"
        "1️⃣ Укажите ваш возраст (только число):",
    )


async def collect_init_Q2(message: Message):
    await message.answer("⚖️ Ваш вес (в кг):\n<i>Введите только число, например: 68</i>")


async def collect_init_Q3(message: Message):
    await message.answer(
        "📏 Ваш рост (в см):\n<i>Введите только число, например: 175</i>"
    )


async def collect_init_Q4(message: Message):
    await message.answer(
        "👤 Укажите ваш пол:\n\n"
        "♂️ Мужской - отправьте <b>М</b>\n"
        "♀️ Женский - отправьте <b>Ж</b>\n\n"
        "<i>Отправьте одну букву: м или ж</i>",
    )


def calc_calories(init_users: dict) -> int:
    age = init_users["age"]
    if age < 10:
        return 2000
    if 10 < age < 14:
        return 2300
    weight = init_users["weight"]
    height = init_users["height"]
    gender = init_users["gender"]
    if gender == "м":
        oo = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        oo = 10 * weight + 6.25 * height - 5 * age - 161
    return oo * 1.375
