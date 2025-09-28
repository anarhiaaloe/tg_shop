from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram import F
from db import Database

router = Router()

@router.callback_query(F.data == "order:make")
async def make_order(callback: CallbackQuery, **kwargs):
    db: Database = kwargs.get("db")
    user_id = callback.from_user.id
    items = await db.get_cart(user_id)
    if not items:
        await callback.answer("Корзина пуста!", show_alert=True)
        return

    total = 0
    lines = []
    for it in items:
        name = it["name"]
        size = it["size"]
        qty = it["quantity"]
        price = float(it["price"])
        total += price * qty
        lines.append(f"{name} ({size}) x{qty}")

    order_id = await db.create_order(user_id, total)
    await db.clear_cart(user_id)
    text = f"✅ Заказ #{order_id} оформлен!\n\n" + "\n".join(lines) + f"\n\n💰 Сумма: {int(total)}₽"
    await callback.message.edit_text(text)
    await callback.answer()
