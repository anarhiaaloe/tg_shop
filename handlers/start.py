from aiogram import types
from db import add_user
from keyboards import main_menu

async def start_cmd(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer("Добро пожаловать в магазин!", reply_markup=main_menu())
