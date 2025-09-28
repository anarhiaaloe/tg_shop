import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from config import API_TOKEN, DB_URL
from db import Database
from handlers import router as handlers_router

class DBMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

    async def __call__(self, handler, event, data):
        # data передаётся в handlers как kwargs
        data["db"] = self.db
        return await handler(event, data)

async def main():
    if not API_TOKEN:
        raise RuntimeError("API_TOKEN not set in .env")
    db = await Database.create(DB_URL)

    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # middleware
    dp.message.middleware(DBMiddleware(db))
    dp.callback_query.middleware(DBMiddleware(db))

    # include routers
    dp.include_router(handlers_router)

    print("🤖 Bot started")
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
