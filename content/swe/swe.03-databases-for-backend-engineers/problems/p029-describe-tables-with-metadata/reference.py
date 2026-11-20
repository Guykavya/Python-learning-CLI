from sqlalchemy import Column, ForeignKey, Integer, String, Table


def make_tables(metadata):
    customers = Table(
        "customers", metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(100), nullable=False),
        Column("city", String(50)),
        Column("email", String(200), nullable=False, unique=True),
    )
    orders = Table(
        "orders", metadata,
        Column("id", Integer, primary_key=True),
        Column("customer_id", Integer, ForeignKey("customers.id"), nullable=False),
        Column("total_paise", Integer, nullable=False),
        Column("status", String(20), nullable=False, server_default="open"),
    )
    return customers, orders
