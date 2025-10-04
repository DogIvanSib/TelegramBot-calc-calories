import logging
from copy import deepcopy

from aiogram.types import Message

logger = logging.getLogger()


async def collect_init_from_user(
    users: dict, init_users: dict, message: Message
) -> bool:
    "Собираю инфу о пользователе"
    user_id = message.from_user.id
    answer = message.text
    if user_id in users:
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
        users |= deepcopy(init_users)
        del init_users[user_id]
        logger.info(f"users=={users}")
        return True
    logger.debug(f"init_users=={init_users}")

    return False


async def collect_init_Q1(message: Message):
    await message.answer("Ваш возраст в годах(только число):")


async def collect_init_Q2(message: Message):
    await message.answer("Вес в кг (только число):")


async def collect_init_Q3(message: Message):
    await message.answer("Рост в см (только число):")
