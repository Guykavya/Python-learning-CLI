from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload


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


def customer_summary(engine, customer_id):
    with Session(engine) as session:
        customer = session.scalars(
            select(Customer).where(Customer.id == customer_id).options(selectinload(Customer.orders))
        ).one_or_none()
        if customer is None:
            return None
        return {
            "id": customer.id,
            "name": customer.name,
            "orders": [{"id": o.id, "total_paise": o.total_paise} for o in sorted(customer.orders, key=lambda o: o.id)],
        }
