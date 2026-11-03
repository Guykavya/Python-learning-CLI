# Normalise a flat table into three tables

A *flat* table that repeats facts (the customer's city on every line, a book's price on every line) invites update mistakes: change Ada's city in one row and
the others disagree. Normalising means each fact is stored once, and rows point to each other with keys.

The test gives you this flat table (other data is used too):

```sql
CREATE TABLE orders_flat (order_id INTEGER, customer_name TEXT, customer_city TEXT, book_title TEXT, book_price REAL, qty INTEGER);
INSERT INTO orders_flat VALUES
 (1,'Ada','Pune','Rust Basics',30,1),(1,'Ada','Pune','Go Tour',20,2),(2,'Bo','Oslo','Rust Basics',30,1),(3,'Ada','Pune','Go Tour',20,1);
```

Write `SCRIPT` that creates three tables, fills them from `orders_flat`, and leaves `orders_flat` alone:

| table | columns | rules |
|---|---|---|
| `customers` | `customer_id` (integer primary key), `name`, `city` | one row per distinct customer; `name` is `NOT NULL UNIQUE`; `city` may be NULL |
| `books` | `book_id` (integer primary key), `title`, `price` | one row per distinct title; `title` is `NOT NULL UNIQUE`; `price` is `NOT NULL` |
| `lines` | `line_id` (integer primary key), `order_id`, `customer_id`, `book_id`, `qty` | one row per flat row; `customer_id` references `customers`, `book_id` references `books`; all `NOT NULL` |

Let SQLite choose the ids. A customer's name identifies them; each title has one price.
Fill `lines` by joining back to the new tables to find the ids.

**Example**

For the data above: `customers` has 2 rows (Ada, Bo), `books` has 2 rows (Rust Basics, Go Tour), `lines` has 4 rows. Joining the three tables must give back exactly the 4 flat rows.
