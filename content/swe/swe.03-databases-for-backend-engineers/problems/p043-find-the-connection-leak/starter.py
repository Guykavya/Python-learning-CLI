from sqlalchemy import text


def lookup(engine, user_id):
    conn = engine.connect()
    row = conn.execute(text("SELECT name FROM users WHERE id = :id"), {"id": user_id}).first()
    if row is None:
        raise KeyError(user_id)            # BUG: the connection is never returned to the pool on this path
    conn.close()
    return row[0]
