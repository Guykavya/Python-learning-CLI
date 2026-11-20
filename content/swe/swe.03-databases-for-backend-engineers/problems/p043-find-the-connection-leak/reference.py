from sqlalchemy import text


def lookup(engine, user_id):
    with engine.connect() as conn:                       # closed (returned to the pool) on every path
        row = conn.execute(text("SELECT name FROM users WHERE id = :id"), {"id": user_id}).first()
        if row is None:
            raise KeyError(user_id)
        return row[0]
