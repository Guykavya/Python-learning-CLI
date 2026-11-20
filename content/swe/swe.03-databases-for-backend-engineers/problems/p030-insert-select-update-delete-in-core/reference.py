from sqlalchemy import Column, Integer, MetaData, String, Table, delete, insert, select, update

metadata = MetaData()
customers = Table(
    "customers", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("city", String(50)),
)


def add_many(engine, rows):
    if not rows:
        return 0
    with engine.begin() as conn:
        return conn.execute(insert(customers), rows).rowcount


def by_city(engine, city):
    with engine.connect() as conn:
        return list(conn.scalars(select(customers.c.name).where(customers.c.city == city).order_by(customers.c.name)))


def rename(engine, customer_id, new_name):
    with engine.begin() as conn:
        return conn.execute(update(customers).where(customers.c.id == customer_id).values(name=new_name)).rowcount


def remove(engine, customer_id):
    with engine.begin() as conn:
        return conn.execute(delete(customers).where(customers.c.id == customer_id)).rowcount
