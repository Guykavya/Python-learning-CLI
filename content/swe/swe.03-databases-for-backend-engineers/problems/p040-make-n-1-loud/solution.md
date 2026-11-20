## Approach

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, joinedload, mapped_column, relationship, selectinload
from sqlalchemy import select


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    orders: Mapped[list["Order"]] = relationship(back_populates="customer", lazy="raise")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(back_populates="orders", lazy="raise")
    lines: Mapped[list["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan", lazy="raise")


class OrderLine(Base):
    __tablename__ = "order_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    sku: Mapped[str] = mapped_column(String(20))
    order: Mapped["Order"] = relationship(back_populates="lines", lazy="raise")


def naive_report(session):
    """The code that used to work with lazy loading: now it raises instead of running N+1 queries."""
    return [(o.id, o.customer.name, len(o.lines)) for o in session.scalars(select(Order).order_by(Order.id))]


def report(session):
    query = (select(Order).order_by(Order.id)
             .options(joinedload(Order.customer), selectinload(Order.lines)))
    return [(o.id, o.customer.name, len(o.lines)) for o in session.scalars(query)]
```

`lazy="raise"` makes the **default** "never load behind my back". A query that needs a relationship asks for it with an option; the option wins over the model's setting for that query only. The many-to-one `customer` is joined in the first statement (one row per order), the collection `lines` is loaded by one `IN` query: two statements for any number of orders.

Example: forgetting `selectinload(Order.lines)` makes `len(o.lines)` raise `InvalidRequestError` in the very first test run, not in production under load.

## Complexity

2 queries.

## Another way

`lazy="raise_on_sql"` raises only when a lazy load would need SQL (an object already in the identity map is still allowed). `lazy="raise"` is the strictest.

## Why it matters

A loud failure in development is cheaper than a slow page in production. Many teams set `lazy="raise"` on every relationship and opt in per query.
