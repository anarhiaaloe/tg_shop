from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message, state=None, **kwargs):
    await message.answer(
        "👋 Привет! Это тестовый магазин.\n\n"
        "Команды:\n"
        "/catalog — Показать каталог\n"
        "/cart — Показать корзину"
    )
