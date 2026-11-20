from sqlalchemy import Column, ForeignKey, Integer, String, Table


def make_tables(metadata):
    # TODO: two Table objects on `metadata`, with types, primary keys, unique, not null, ForeignKey, server_default
    customers = Table("customers", metadata, Column("id", Integer, primary_key=True))
    orders = Table("orders", metadata, Column("id", Integer, primary_key=True))
    return customers, orders
