import asyncio


async def use_resource(pool, work):
    """Borrow a connection, run work(conn), and always give the connection back."""
    conn = await pool.acquire()
    try:
        return await work(conn)
    finally:
        pool.release(conn)
