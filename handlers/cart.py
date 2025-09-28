from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from keyboards import cart_keyboard, cart_item_keyboard
from db import Database

router = Router()

@router.message(Command("cart"))
async def show_cart(message: Message, **kwargs):
    db: Database = kwargs.get("db")
    user_id = message.from_user.id
    items = await db.get_cart(user_id)
    if not items:
        await message.answer("🛒 Ваша корзина пуста.")
        return

    lines = ["🛒 Ваша корзина:\n"]
    total = 0
    for it in items:
        name = it["name"]
        size = it["size"]
        qty = it["quantity"]
        price = float(it["price"])
        subtotal = int(price * qty)
        total += price * qty
        lines.append(f"{name} ({size}) x{qty} = {subtotal}₽")
    lines.append(f"\n💰 Итого: {int(total)}₽")
    await message.answer("\n".join(lines), reply_markup=cart_keyboard())

@router.callback_query(F.data == "cart:clear")
async def clear_cart(callback: CallbackQuery, **kwargs):
    db: Database = kwargs.get("db")
    user_id = callback.from_user.id
    await db.clear_cart(user_id)
    await callback.message.edit_text("🗑 Корзина очищена.")
    await callback.answer()

@router.callback_query(F.data.startswith("cart:remove:"))
async def remove_item(callback: CallbackQuery, **kwargs):
    db: Database = kwargs.get("db")
    parts = callback.data.split(":")
    # формат cart:remove:<product_id>:<size>
    if len(parts) != 4:
        await callback.answer("Неверные данные", show_alert=True)
        return
    product_id = int(parts[2])
    size = parts[3]
    user_id = callback.from_user.id
    await db.remove_cart_item(user_id, product_id, size)
    await callback.answer("Удалено из корзины")
    # обновим текст сообщения для простоты
    await callback.message.edit_text("Элемент удалён. Введите /cart чтобы посмотреть корзину.")
