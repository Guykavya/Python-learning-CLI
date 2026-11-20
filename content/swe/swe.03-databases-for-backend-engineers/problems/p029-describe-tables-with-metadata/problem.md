# Describe tables with `MetaData`

Chapter section 8.2. In SQLAlchemy Core a **table** is a Python object that describes the real one. Write

```python
make_tables(metadata)      # -> (customers, orders)
```

which defines two `Table` objects on the given `MetaData` and returns them:

| Table `customers` | |
|---|---|
| `id` | `Integer`, primary key |
| `name` | `String(100)`, not null |
| `city` | `String(50)`, may be null |
| `email` | `String(200)`, not null, **unique** |

| Table `orders` | |
|---|---|
| `id` | `Integer`, primary key |
| `customer_id` | `Integer`, **foreign key** to `customers.id`, not null |
| `total_paise` | `Integer`, not null |
| `status` | `String(20)`, not null, with the **server default** `'open'` |

After `metadata.create_all(engine)` the tests inspect the database with `sqlalchemy.inspect` and insert rows (an order without `status` must get `open`).
