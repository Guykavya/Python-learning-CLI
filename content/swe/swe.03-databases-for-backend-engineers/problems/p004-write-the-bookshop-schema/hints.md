## Hint 1

One `CREATE TABLE` per table. Which clause makes a column unique? Which one forbids `NULL`? Which one links a column to another table's key?

## Hint 2

`CHECK (qty > 0)` is a column or table rule. A foreign key can be written inline: `customer_id INTEGER NOT NULL REFERENCES customers(id)`. A key over two columns is a table-level `PRIMARY KEY (a, b)`.

## Hint 3

```text
customers: id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL
books:     ... price_paise INTEGER NOT NULL CHECK (price_paise >= 0)
orders:    customer_id INTEGER NOT NULL REFERENCES customers(id)
order_lines: PRIMARY KEY (order_id, book_id), qty CHECK (qty > 0) ...
```
