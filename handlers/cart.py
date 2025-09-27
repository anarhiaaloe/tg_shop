from aiogram import types
from db import get_cart, get_user

async def show_cart(message: types.Message):
    user = await get_user(message.from_user.id)
    rows = await get_cart(user["id"])
    if not rows:
        await message.answer("🛒 Корзина пуста")
        return

    total = 0
    text = "🛒 Ваша корзина:\n\n"
    for r in rows:
        text += f"{r['name']} — {r['price']} ₽ x {r['quantity']}\n"
        total += r['price'] * r['quantity']

    text += f"\n💰 Итого: {total} ₽"
    await message.answer(text)
