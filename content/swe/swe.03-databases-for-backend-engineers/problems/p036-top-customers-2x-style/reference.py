from sqlalchemy import ForeignKey, String, func, select
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


def top_customers(session, n):
    query = (
        select(Customer.name, func.count(Order.id).label("orders"), func.sum(Order.total_paise).label("total"))
        .join(Order, Order.customer_id == Customer.id)
        .group_by(Customer.id, Customer.name)
        .order_by(func.sum(Order.total_paise).desc(), Customer.name)
        .limit(n)
    )
    return [tuple(row) for row in session.execute(query)]
