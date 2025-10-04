import logging

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from secret import TOKEN
from answers import START_BUTTON
from handlers.user_init import collect_init_from_user

dp = Dispatcher()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # level=logging.INFO,
    level=logging.DEBUG,
)
logger = logging.getLogger()

users = {}  # авторизованные пользователи с информацией
init_users = {}  # в процессе авторизации


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(START_BUTTON)


@dp.message(F.text.regexp(r".*"))
async def receive_answer(message: Message) -> None:
    global users, init_users
    init_user = await collect_init_from_user(users, init_users, message)
    if init_user:
        logger.debug(f"Message: {message.text}")
        pass


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
