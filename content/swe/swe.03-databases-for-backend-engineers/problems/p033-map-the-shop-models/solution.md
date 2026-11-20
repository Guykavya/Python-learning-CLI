## Approach

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    total_paise: Mapped[int] = mapped_column(default=0)
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    lines: Mapped[list["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderLine(Base):
    __tablename__ = "order_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    sku: Mapped[str] = mapped_column(String(20))
    qty: Mapped[int]
    price_paise: Mapped[int]
    order: Mapped["Order"] = relationship(back_populates="lines")
```

`Mapped[int]` gives an integer column that is `NOT NULL` (because the type is not `Optional`). `ForeignKey` on the many side stores the link; `relationship` gives the Python view of it, and `back_populates` keeps both sides in step: appending to `customer.orders` sets `order.customer`. `cascade="all, delete-orphan"` on `Order.lines` says that a line **belongs** to its order: saving the order saves the lines, deleting the order deletes them, and a line removed from the list (orphaned) is deleted.

Example: `session.add(c)` reaches the orders and lines through the relationships (the `save-update` part of the cascade), so one `add` inserts three rows in the right order.

## Complexity

Not applicable.

## Another way

Without `delete-orphan`, removing a line from `order.lines` would try to set its `order_id` to `NULL` (and fail on a `NOT NULL` column). Without any cascade you must `session.add` every object yourself.

## Why it matters

These models are the base of the next problems (identity map, N+1, sessions) and of the project. A relationship with the wrong cascade is a classic source of orphan rows or surprising deletes.
