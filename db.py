import asyncpg
from config import DB_URL

pool = None

async def create_pool():
    global pool
    pool = await asyncpg.create_pool(DB_URL)
    return pool

async def add_user(tg_id, username):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (tg_id, username) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            tg_id, username
        )

async def get_products():
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM products")

async def add_to_cart(user_id, product_id):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES ($1, $2, 1)",
            user_id, product_id
        )

async def get_cart(user_id):
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT p.name, p.price, c.quantity
            FROM cart c
            JOIN products p ON p.id=c.product_id
            WHERE c.user_id=$1
        """, user_id)

async def get_user(tg_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE tg_id=$1", tg_id)
