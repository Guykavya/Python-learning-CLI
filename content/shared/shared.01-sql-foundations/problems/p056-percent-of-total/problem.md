# Percent of category and of everything

A window `SUM(price) OVER ()` (empty parentheses) is the grand total repeated on every row, and `SUM(price) OVER (PARTITION BY category)` is the total of the row's own category.
Dividing a row's value by these gives a share, with no `GROUP BY` and no self join.

```sql
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
INSERT INTO books VALUES (1,'Rust Basics','Tech',30),(2,'Go Tour','Tech',20),(3,'Tales','Fiction',10),(4,'Epic','Fiction',30),(5,'Atlas','Maps',40);
```

Write one `SELECT` returning `title`, `category`, `price`, `pct_category`, `pct_all`:
the book's price as a percentage of its category's total price, and as a percentage of the total price of all books, each `ROUND`ed to 1 decimal.
Order by `book_id`. Use `100.0 * price / total` so the division is not an integer division.

**Example**

| title | category | price | pct_category | pct_all |
|---|---|---|---|---|
| Rust Basics | Tech | 30.0 | 60.0 | 23.1 |
| Go Tour | Tech | 20.0 | 40.0 | 15.4 |
| Tales | Fiction | 10.0 | 25.0 | 7.7 |
| Epic | Fiction | 30.0 | 75.0 | 23.1 |
| Atlas | Maps | 40.0 | 100.0 | 30.8 |
