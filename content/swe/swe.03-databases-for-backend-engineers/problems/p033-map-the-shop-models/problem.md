# Map the shop models

Chapter section 9.2. Write the three model classes of the shop in `solution.py` (and a `Base`), with **exactly these names**:

| Class (`__tablename__`) | Columns | Relationships |
|---|---|---|
| `Customer` (`customers`) | `id` (int, primary key), `name` (`String(100)`) | `orders`: list of `Order`, `back_populates="customer"` |
| `Order` (`orders`) | `id`, `customer_id` (foreign key to `customers.id`), `total_paise` (int, default 0) | `customer` (`back_populates="orders"`); `lines`: list of `OrderLine`, `back_populates="order"`, **`cascade="all, delete-orphan"`** |
| `OrderLine` (`order_lines`) | `id`, `order_id` (foreign key to `orders.id`), `sku` (`String(20)`), `qty` (int), `price_paise` (int) | `order` (`back_populates="lines"`) |

Use the SQLAlchemy 2.x style: `DeclarativeBase`, `Mapped[...]`, `mapped_column(...)`, `relationship(...)`.

The tests check that building a customer with orders and lines and calling **one** `session.add(customer)` saves everything, that deleting an order deletes its lines, and that removing a line from `order.lines` deletes it (`delete-orphan`).

## Example

```python
c = Customer(name="Asha", orders=[Order(lines=[OrderLine(sku="TEA", qty=2, price_paise=25000)])])
session.add(c); session.commit()      # three rows in three tables
```
