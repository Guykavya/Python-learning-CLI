## Approach

```python
import os
import sqlite3

from sqlalchemy import CheckConstraint, ForeignKey, String, create_engine, event, func, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    name: Mapped[str] = mapped_column(String(100))


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("price_paise >= 0", name="price_not_negative"),
                      CheckConstraint("stock >= 0", name="stock_not_negative"))
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(30), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    price_paise: Mapped[int]
    stock: Mapped[int]
    version: Mapped[int] = mapped_column(default=1)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    total_paise: Mapped[int] = mapped_column(default=0)
    lines: Mapped[list["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderLine(Base):
    __tablename__ = "order_lines"
    __table_args__ = (CheckConstraint("qty > 0", name="qty_positive"),
                      CheckConstraint("unit_price_paise >= 0", name="unit_price_not_negative"))
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty: Mapped[int]
    unit_price_paise: Mapped[int]
    order: Mapped["Order"] = relationship(back_populates="lines")


class OutOfStock(ValueError):
    pass


class RestoreFailed(Exception):
    pass


def make_engine(path):
    engine = create_engine(f"sqlite:///{path}")

    @event.listens_for(engine, "connect")
    def _foreign_keys_on(dbapi_connection, record):
        dbapi_connection.execute("PRAGMA foreign_keys = ON")

    Base.metadata.create_all(engine)
    return engine


def seed(session):
    session.add_all([
        Customer(email="asha@x.com", name="Asha"), Customer(email="ravi@x.com", name="Ravi"),
        Customer(email="meena@x.com", name="Meena"),
        Product(sku="TEA", name="Green Tea", price_paise=25000, stock=10),
        Product(sku="COF", name="Coffee", price_paise=30000, stock=5),
        Product(sku="MUG", name="Mug", price_paise=45000, stock=3),
        Product(sku="BOOK", name="Notebook", price_paise=15000, stock=20),
        Product(sku="PEN", name="Pen", price_paise=500, stock=100),
    ])
    session.commit()


def place_order(session, customer_id, items):
    if not items:
        raise ValueError("an order needs at least one item")
    if session.get(Customer, customer_id) is None:
        raise LookupError(f"no customer {customer_id}")
    with session.begin_nested():                                  # a failure undoes the whole order, not the session
        order = Order(customer_id=customer_id)
        session.add(order)
        session.flush()
        total = 0
        for sku, qty in items:
            if qty <= 0:
                raise ValueError("quantities must be positive")
            product = session.execute(select(Product.id, Product.price_paise).where(Product.sku == sku)).first()
            if product is None:
                raise LookupError(f"no product {sku}")
            taken = session.execute(
                update(Product).where(Product.id == product.id, Product.stock >= qty)
                .values(stock=Product.stock - qty, version=Product.version + 1)
                .execution_options(synchronize_session=False))
            if taken.rowcount == 0:                               # checked and decremented in ONE statement
                raise OutOfStock(sku)
            session.add(OrderLine(order_id=order.id, product_id=product.id, qty=qty, unit_price_paise=product.price_paise))
            total += qty * product.price_paise
        order.total_paise = total
    session.commit()
    return order.id


def orders_with_totals(session):
    query = (select(Order.id, Customer.name, func.sum(OrderLine.qty * OrderLine.unit_price_paise), func.count(OrderLine.id))
             .join(Customer, Customer.id == Order.customer_id)
             .join(OrderLine, OrderLine.order_id == Order.id)
             .group_by(Order.id, Customer.name)
             .order_by(Order.id))
    return [tuple(row) for row in session.execute(query)]


def backup(src_path, dst_path):
    if os.path.exists(dst_path):
        raise FileExistsError(dst_path)
    source = sqlite3.connect(src_path)
    target = sqlite3.connect(dst_path)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()


def fingerprint(conn):
    result = {}
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    for table in tables:
        numeric = [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")') if r[2].upper() in ("INTEGER", "REAL")]
        sums = {c: conn.execute(f'SELECT COALESCE(SUM("{c}"), 0) FROM "{table}"').fetchone()[0] for c in numeric}
        result[table] = {"rows": conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0], "sums": sums}
    return result


def restore_and_verify(backup_path, expected, dest_path):
    if os.path.exists(dest_path):
        raise FileExistsError(dest_path)
    try:
        source = sqlite3.connect(backup_path)
        if source.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise RestoreFailed("the backup fails the integrity check")
        dest = sqlite3.connect(dest_path)
        source.backup(dest)
        source.close()
        actual = fingerprint(dest)
        dest.close()
    except sqlite3.DatabaseError as exc:
        raise RestoreFailed(f"the backup cannot be read: {exc}") from exc
    differences = sorted(t for t in set(expected) | set(actual) if expected.get(t) != actual.get(t))
    if differences:
        raise RestoreFailed("tables differ after the restore: " + ", ".join(differences))
    return actual
```

How the pieces answer the course:

- **Schema** (sections 3 and 4): constraints in the database (`CHECK`, `UNIQUE`, foreign keys with the pragma on), money in paise, the order line keeps the price at sale time.
- **Transactions and concurrency** (6 and 7): the stock check and the decrement are one `UPDATE`; another session that already took the stock makes `rowcount` 0 even though this session's loaded `Product` object is stale. A **savepoint** makes the order all-or-nothing without ruining the session.
- **Queries** (8 to 10): `orders_with_totals` joins and groups in the database: one statement, no N+1.
- **Backups** (15): the online backup API, and a restore into a fresh file that is checked with a fingerprint.

Example: `place_order(s, 1, [("TEA", 2), ("MUG", 1)])` stores 2 x 25000 + 45000 = 95000 paise, lowers the two stocks, and returns the order id; `place_order(s, 1, [("TEA", 1), ("MUG", 99)])` raises `OutOfStock` and leaves the TEA stock as it was.

## Complexity

`place_order`: `O(items)` statements. `orders_with_totals`: one statement.

## Another way

Wrap this in FastAPI routes (swe.05), use PostgreSQL in production (the same SQLAlchemy code, with `SELECT ... FOR UPDATE` or the same atomic update), and run the migrations with Alembic (problems 45 to 48).

## Why it matters

Each part is small; together they are what "a database you can trust" means: it refuses bad data, never sells what it does not have, answers pages in a constant number of queries, and can be restored.
