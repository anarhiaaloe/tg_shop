from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards import cart_keyboard, cart_item_keyboard
from db import Database

router = Router()


# --- Показать корзину ---
@router.message(Command("cart"))
async def show_cart(message: Message, db: Database):
    user = message.from_user

    # ✅ гарантируем, что пользователь есть в БД
    await db.ensure_user(
        tg_id=user.id,
        username=user.username,
        full_name=user.full_name,
    )

    items = await db.get_cart(user.id)

    if not items:
        await message.answer("🛒 Ваша корзина пуста.")
        return

    total = 0
    for it in items:
        subtotal = int(float(it["price"]) * it["quantity"])
        total += subtotal

        caption = (
            f"📦 <b>{it['name']}</b>\n"
            f"Размер: {it['size']}\n"
            f"Количество: {it['quantity']}\n"
            f"💰 Цена: {subtotal}₽"
        )

        await message.answer_photo(
            photo=it["image_url"],
            caption=caption,
            parse_mode="HTML",
            reply_markup=cart_item_keyboard(it["product_id"], it["size"])
        )

    await message.answer(
        f"💰 <b>Итого:</b> {int(total)}₽",
        parse_mode="HTML",
        reply_markup=cart_keyboard()
    )


# --- Очистка корзины ---
@router.callback_query(F.data == "cart:clear")
async def clear_cart(callback: CallbackQuery, db: Database):
    # ✅ убедимся, что юзер в БД
    await db.ensure_user(
        tg_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name,
    )

    await db.clear_cart(callback.from_user.id)
    await callback.message.edit_text("🗑 Корзина очищена.")
    await callback.answer()


# --- Удаление товара ---
@router.callback_query(F.data.startswith("cart:remove:"))
async def remove_item(callback: CallbackQuery, db: Database):
    parts = callback.data.split(":")
    # формат cart:remove:<product_id>:<size>
    if len(parts) != 4:
        await callback.answer("Неверные данные", show_alert=True)
        return

    product_id = int(parts[2])
    size = parts[3]

    # ✅ убедимся, что юзер в БД
    await db.ensure_user(
        tg_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name,
    )

    await db.remove_cart_item(callback.from_user.id, product_id, size)
    await callback.answer("Удалено из корзины")

    await callback.message.edit_text("❌ Товар удалён.\nВведите /cart чтобы обновить корзину.")
