## Hint 1

A class that inherits from a `DeclarativeBase` subclass becomes a table. Each column is an annotation `name: Mapped[type] = mapped_column(...)`.

## Hint 2

A relationship is declared on **both** sides, and `back_populates` names the attribute on the other side, so that changing one side updates the other in Python. The foreign key lives on the "many" side.

## Hint 3

```text
class Customer(Base): orders: Mapped[list["Order"]] = relationship(back_populates="customer")
class Order(Base): customer_id FK; customer = relationship(back_populates="orders");
                   lines = relationship(back_populates="order", cascade="all, delete-orphan")
class OrderLine(Base): order_id FK; order = relationship(back_populates="lines")
```
