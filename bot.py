import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from config import API_TOKEN
from db import create_pool, get_user, add_to_cart, get_products
from handlers import start, catalog, cart
from keyboards import main_menu

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация хэндлеров
dp.message.register(start.start_cmd, Command("start"))
dp.message.register(catalog.show_catalog, lambda m: m.text == "🛒 Каталог")
dp.message.register(cart.show_cart, lambda m: m.text == "📦 Корзина")

# Обработка inline-кнопки "Купить"
@dp.callback_query(F.data.startswith("buy:"))
async def buy_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(":")[1])

    user = await get_user(callback.from_user.id)
    products = await get_products()
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        await callback.answer("❌ Такого товара нет", show_alert=True)
        return

    await add_to_cart(user["id"], product_id)
    await callback.answer(f"✅ {product['name']} добавлен в корзину!", show_alert=True)

async def main():
    await create_pool()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
