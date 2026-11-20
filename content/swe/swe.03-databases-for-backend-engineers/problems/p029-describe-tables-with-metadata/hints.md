## Hint 1

`Table(name, metadata, Column(...), Column(...))`: the first argument is the SQL name, the second the metadata object, then the columns.

## Hint 2

Constraints are arguments of `Column`: `primary_key=True`, `nullable=False`, `unique=True`, `ForeignKey("customers.id")` as the second positional argument, `server_default="open"`.

## Hint 3

```text
customers = Table("customers", metadata, Column("id", Integer, primary_key=True), Column("name", String(100), nullable=False), ...)
orders = Table("orders", metadata, ..., Column("customer_id", Integer, ForeignKey("customers.id"), nullable=False), ...,
               Column("status", String(20), nullable=False, server_default="open"))
return customers, orders
```
