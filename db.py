import asyncpg
from typing import Optional, List, Any
from config import DB_URL


class Database:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    @classmethod
    async def create(cls, dsn: Optional[str] = None):
        dsn = dsn or DB_URL
        pool = await asyncpg.create_pool(
            dsn,
            min_size=1,
            max_size=10,
            command_timeout=60,
            max_inactive_connection_lifetime=300
        )
        return cls(pool)

    async def close(self):
        await self.pool.close()

    # --- Users ---
    async def ensure_user(self, tg_id: int, username: Optional[str] = None):
        """
        Вставляет пользователя в users если ещё нет (tg_id уникален).
        """
        await self.pool.execute(
            """
            INSERT INTO users (tg_id, username)
            VALUES ($1, $2)
            ON CONFLICT (tg_id) DO UPDATE SET username = EXCLUDED.username
            """,
            tg_id, username
        )

    # --- Products ---
    async def get_products(self) -> List[asyncpg.Record]:
        return await self.pool.fetch("SELECT * FROM products ORDER BY id")

    async def get_product(self, product_id: int) -> Optional[asyncpg.Record]:
        return await self.pool.fetchrow("SELECT * FROM products WHERE id=$1", product_id)

    # --- Cart ---
    async def add_to_cart(self, user_id: int, product_id: int, quantity: int, size: str):
        async with self.pool.acquire() as conn:
            # Проверим, есть ли уже такой товар с этим размером
            row = await conn.fetchrow(
                "SELECT id, quantity FROM cart WHERE user_id=$1 AND product_id=$2 AND size=$3",
                user_id, product_id, size
            )
            if row:
                await conn.execute(
                    "UPDATE cart SET quantity=quantity+$1 WHERE id=$2",
                    quantity, row["id"]
                )
            else:
                await conn.execute(
                    "INSERT INTO cart (user_id, product_id, quantity, size) VALUES ($1, $2, $3, $4)",
                    user_id, product_id, quantity, size
                )
    async def get_cart(self, user_tg_id: int) -> List[asyncpg.Record]:
        return await self.pool.fetch(
            """
            SELECT c.id, c.user_id, c.product_id, c.size, c.quantity,
                   p.name, p.price, p.image_url
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = $1
            ORDER BY c.id
            """,
            user_tg_id
        )

    async def clear_cart(self, user_tg_id: int):
        await self.pool.execute("DELETE FROM cart WHERE user_id = $1", user_tg_id)

    async def remove_cart_item(self, user_tg_id: int, product_id: int, size: str):
        await self.pool.execute(
            "DELETE FROM cart WHERE user_id = $1 AND product_id = $2 AND size = $3",
            user_tg_id, product_id, size
        )

    # --- Orders ---
    async def create_order(self, user_tg_id: int, total: float) -> int:
        return await self.pool.fetchval(
            "INSERT INTO orders (user_id, created_at, total) VALUES ($1, NOW(), $2) RETURNING id",
            user_tg_id, total
        )
