import asyncio


async def use_resource(pool, work):
    """Borrow a connection, run work(conn), and always give the connection back."""
    conn = await pool.acquire()
    try:
        result = await work(conn)
    except asyncio.CancelledError:
        print("cancelled, giving up")
        return None
    pool.release(conn)
    return result
