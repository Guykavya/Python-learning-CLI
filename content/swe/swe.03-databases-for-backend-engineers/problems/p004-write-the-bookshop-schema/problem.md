# Write the bookshop schema

Write the string `SCHEMA` in `solution.py`: SQL (several statements) that creates a bookshop database with **exactly these tables and columns** and with every rule enforced **by the database** (chapter sections 3 and 4):

| Table | Columns | Rules |
|---|---|---|
| `customers` | `id`, `email`, `name` | `id` primary key; `email` and `name` not null; `email` unique |
| `books` | `id`, `title`, `price_paise` | `id` primary key; `title` not null; `price_paise` integer, not null, **at least 0** |
| `orders` | `id`, `customer_id`, `placed_at` | `id` primary key; `customer_id` not null, **references** `customers(id)`; `placed_at` text, not null |
| `order_lines` | `order_id`, `book_id`, `qty`, `price_paise` | primary key `(order_id, book_id)`; both ids not null and **foreign keys**; `qty` integer not null, **greater than 0**; `price_paise` integer not null, at least 0 |

Money is in **paise** (integers), never floats. The tests run `SCHEMA` with `executescript` on an in-memory SQLite database with `PRAGMA foreign_keys = ON`, check the tables and columns with `PRAGMA table_info` and `PRAGMA foreign_key_list`, and then try six bad inserts: each must be refused **for the right reason** (`UNIQUE`, `NOT NULL`, `CHECK`, `FOREIGN KEY`).
