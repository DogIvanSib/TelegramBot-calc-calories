from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Маленькая", callback_data="product_save_small"),
            InlineKeyboardButton(text="Средняя", callback_data="product_save_midle"),
            InlineKeyboardButton(text="Большая", callback_data="product_save_big"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_photo():
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Внести запись", callback_data="product_save_photo"
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
