from sqlalchemy import text


def find_user(conn, name):
    # BUG: the name is pasted into the SQL text
    return list(conn.exec_driver_sql(f"SELECT id, name FROM users WHERE name = '{name}'"))
