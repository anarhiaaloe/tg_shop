from aiogram import types, Router
from db import get_products
from keyboards import product_keyboard

router = Router()

async def show_catalog(message: types.Message):
    products = await get_products()
    if not products:
        await message.answer("❌ Каталог пуст")
        return

    for product in products:
        text = f"📦 {product['name']}\n💰 Цена: {product['price']}₽"
        await message.answer(
            text,
            reply_markup=product_keyboard(product["id"])
        )
