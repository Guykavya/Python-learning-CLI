from sqlalchemy import Column, Integer, MetaData, String, Table, delete, insert, select, update

metadata = MetaData()
customers = Table(
    "customers", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("city", String(50)),
)


def add_many(engine, rows):
    # TODO: with engine.begin() as conn: conn.execute(insert(customers), rows)
    return 0


def by_city(engine, city):
    return []


def rename(engine, customer_id, new_name):
    return 0


def remove(engine, customer_id):
    return 0
