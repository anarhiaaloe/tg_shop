from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards import catalog_keyboard, size_keyboard
from db import Database

router = Router()


# --- Каталог ---
@router.message(Command("catalog"))
async def show_catalog(message: Message, db: Database):
    products = await db.get_products()
    if not products:
        await message.answer("Каталог пуст.")
        return

    await message.answer("🛍 Каталог:", reply_markup=catalog_keyboard(products))


# --- Просмотр товара ---
@router.callback_query(F.data.startswith("product:"))
async def show_product(callback: CallbackQuery, db: Database):
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


# --- Добавление в корзину ---
@router.callback_query(F.data.startswith("choose_size:"))
async def add_to_cart(callback: CallbackQuery, db: Database):
    _, product_id, size = callback.data.split(":")
    product_id = int(product_id)

    user = callback.from_user

    # ✅ гарантируем, что пользователь есть в БД
    await db.ensure_user(
        tg_id=user.id,
        username=user.username,
        full_name=user.full_name,
    )

    # ✅ теперь можно добавить товар в корзину
    await db.add_to_cart(
        user_id=user.id,
        product_id=product_id,
        quantity=1,
        size=size,
    )

    await callback.answer("✅ Добавлено в корзину")
