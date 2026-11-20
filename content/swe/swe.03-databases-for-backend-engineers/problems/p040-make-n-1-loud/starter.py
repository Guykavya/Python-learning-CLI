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
    # TODO: select(Order) with loader options, then build the tuples
    return []
