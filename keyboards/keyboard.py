from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Внести запись", callback_data="product_save")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
