from sqlalchemy import text


def find_user(conn, name):
    result = conn.execute(text("SELECT id, name FROM users WHERE name = :name"), {"name": name})
    return [tuple(row) for row in result]
