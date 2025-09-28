from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def catalog_keyboard(products):
    kb = []
    for p in products:
        kb.append([InlineKeyboardButton(text=f"{p['name']} — {int(p['price'])}₽", callback_data=f"product:{p['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def product_keyboard(product_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать размер", callback_data=f"choose_size:{product_id}")],
        [InlineKeyboardButton(text="⬅️ Назад в каталог", callback_data="back:catalog")]
    ])

def size_keyboard(product_id: int) -> InlineKeyboardMarkup:
    sizes = ["XS", "S", "M", "L", "XL"]
    kb = [
        [InlineKeyboardButton(text=size, callback_data=f"choose_size:{product_id}:{size}")]
        for size in sizes
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def cart_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="order:make")],
        [InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="cart:clear")]
    ])

def cart_item_keyboard(product_id: int, size: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить этот товар", callback_data=f"cart:remove:{product_id}:{size}")],
        [InlineKeyboardButton(text="Изменить размер", callback_data=f"choose_size:{product_id}")]
    ])

def admin_order_keyboard(user_id: int, total: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить заказ",
                    callback_data=f"admin_confirm:{user_id}:{total}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отклонить заказ",
                    callback_data=f"admin_reject:{user_id}"
                )
            ],
        ]
    )