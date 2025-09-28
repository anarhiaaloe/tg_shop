from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db import Database
from keyboards import admin_order_keyboard

router = Router()

# ⚠️ замени на реальный Telegram ID пользователя @Mops_thedog
ADMIN_ID = 724118384


# --- FSM состояния ---
class OrderForm(StatesGroup):
    fio = State()
    address = State()
    postal_code = State()
    wait_delivery_price = State()


# --- начало оформления заказа ---
@router.callback_query(F.data == "order:make")
async def start_order(callback: CallbackQuery, state: FSMContext, db: Database):
    # ✅ гарантируем, что пользователь есть в БД
    await db.ensure_user(
        tg_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name,
    )

    await state.set_state(OrderForm.fio)
    await callback.message.answer("Введите ваше ФИО:")
    await callback.answer()


@router.message(OrderForm.fio)
async def process_fio(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(OrderForm.address)
    await message.answer("Введите адрес проживания:")


@router.message(OrderForm.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(OrderForm.postal_code)
    await message.answer("Введите почтовый индекс:")


@router.message(OrderForm.postal_code)
async def process_postal(message: Message, state: FSMContext, db: Database):
    await state.update_data(postal_code=message.text)
    data = await state.get_data()

    # ✅ ещё раз убедимся, что юзер есть в БД
    await db.ensure_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )

    # Получаем корзину пользователя
    cart = await db.get_cart(message.from_user.id)
    if not cart:
        await message.answer("❌ Ваша корзина пуста.")
        await state.clear()
        return

    # Подсчёт суммы
    total = sum(int(item["price"]) * item["quantity"] for item in cart)

    # Сообщение пользователю
    await message.answer(
        "✅ Ваш заказ принят и обрабатывается.\n"
        "После подтверждения придут реквизиты для оплаты (с учётом доставки)."
    )

    # Формируем текст заказа для админа
    cart_text = "\n".join(
        [
            f"- {item['name']} ({item['size']}) x{item['quantity']} = {int(item['price']) * item['quantity']}₽"
            for item in cart
        ]
    )
    text_for_admin = (
        f"📦 Новый заказ!\n\n"
        f"👤 ФИО: {data['fio']}\n"
        f"🏠 Адрес: {data['address']}\n"
        f"📮 Индекс: {data['postal_code']}\n"
        f"🆔 User ID: {message.from_user.id}\n\n"
        f"Товары:\n{cart_text}\n\n"
        f"Сумма без доставки: {total}₽"
    )

    # Отправляем админу
    await message.bot.send_message(
        ADMIN_ID,
        text_for_admin,
        reply_markup=admin_order_keyboard(message.from_user.id, total),
    )

    await state.clear()


# --- действия админа ---
@router.callback_query(F.data.startswith("admin_reject:"))
async def admin_reject(callback: CallbackQuery):
    _, user_id = callback.data.split(":")
    user_id = int(user_id)

    await callback.bot.send_message(
        user_id,
        "❌ Извините, трудности с вашим заказом.\n"
        "Пожалуйста, свяжитесь с @Mops_thedog",
    )
    await callback.answer("Заказ отклонён.")


@router.callback_query(F.data.startswith("admin_confirm:"))
async def admin_confirm(callback: CallbackQuery, state: FSMContext):
    _, user_id, total = callback.data.split(":")
    user_id, total = int(user_id), int(total)

    await state.update_data(user_id=user_id, total=total)
    await state.set_state(OrderForm.wait_delivery_price)

    await callback.message.answer(
        f"Введите стоимость доставки для заказа пользователя {user_id}:"
    )
    await callback.answer()


@router.message(OrderForm.wait_delivery_price)
async def set_delivery_price(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    user_id = data["user_id"]
    total = data["total"]

    # ✅ убедимся, что пользователь точно есть
    await db.ensure_user(
        tg_id=user_id,
    )

    try:
        delivery = int(message.text)
    except ValueError:
        await message.answer("Введите число (стоимость доставки).")
        return

    final_price = total + delivery
    # отправляем клиенту счёт
    await message.bot.send_message(
        user_id,
        f"✅ Ваш заказ подтверждён!\n\n"
        f"🛒 Сумма товаров: {total}₽\n"
        f"🚚 Доставка: {delivery}₽\n"
        f"💳 Итог к оплате: {final_price}₽\n\n"
        f"Реквизиты для оплаты:\n5469 1234 5678 9999 Сбербанк",
    )

    await message.answer("Счёт отправлен пользователю.")
    await state.clear()
