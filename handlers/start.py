from aiogram import Router, F
from aiogram.types import Message
from db import Database

router = Router()

@router.message(F.text == "/start")
async def start_cmd(message: Message, db: Database):
    # ✅ гарантируем, что юзер есть в БД
    await db.ensure_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    await message.answer("Добро пожаловать в магазин ALL IN ONE")
