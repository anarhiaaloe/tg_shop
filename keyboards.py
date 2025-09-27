from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# Главное меню
def main_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Каталог")],
            [KeyboardButton(text="📦 Корзина")]
        ],
        resize_keyboard=True
    )
    return kb


# Кнопка "Купить" для конкретного товара
def product_keyboard(product_id: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy:{product_id}")]
        ]
    )
    return kb
