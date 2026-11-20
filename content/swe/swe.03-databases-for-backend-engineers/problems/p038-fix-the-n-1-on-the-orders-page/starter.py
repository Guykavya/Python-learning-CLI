from sqlalchemy import ForeignKey, String, select
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


def orders_page(session):
    orders = session.scalars(select(Order).order_by(Order.id).limit(50)).all()
    page = []
    for order in orders:
        page.append({
            "id": order.id,
            "customer": order.customer.name,                                   # one query per order
            "lines": [{"sku": l.sku, "qty": l.qty} for l in sorted(order.lines, key=lambda l: l.id)],   # and another
        })
    return page
