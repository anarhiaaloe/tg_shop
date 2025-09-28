from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from keyboards import catalog_keyboard, product_keyboard, size_keyboard
from db import Database

router = Router()

@router.message(Command("catalog"))
async def show_catalog(message: Message, **kwargs):
    db: Database = kwargs.get("db")
    products = await db.get_products()
    if not products:
        await message.answer("Каталог пуст.")
        return
    await message.answer("🛍 Каталог:", reply_markup=catalog_keyboard(products))

@router.callback_query(F.data.startswith("product:"))
async def show_product(callback: CallbackQuery, **kwargs):
    db: Database = kwargs.get("db")
    product_id = int(callback.data.split(":")[1])
    product = await db.get_product(product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    caption = (
        f"📦 <b>{product['name']}</b>\n"
        f"💰 {int(product['price'])}₽\n\n"
        f"{product['description']}"
    )

    await callback.message.answer_photo(
        photo=product["image_url"],
        caption=caption,
        parse_mode="HTML",
        reply_markup=size_keyboard(product["id"])
    )

@router.callback_query(F.data.startswith("choose_size:"))
async def add_to_cart(callback: CallbackQuery, db: Database):
    _, product_id, size = callback.data.split(":")
    product_id = int(product_id)
    user_id = callback.from_user.id

    # Добавляем в корзину
    await db.add_to_cart(user_id=user_id, product_id=product_id, quantity=1, size=size)

    await callback.answer("✅ Добавлено в корзину")