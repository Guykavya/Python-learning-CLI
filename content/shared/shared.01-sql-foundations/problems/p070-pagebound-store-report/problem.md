# Build: the Pagebound store report

This is the module project. The bookstore database is in `fixtures/store.sql` (about 100 rows). Load it into any SQLite tool to explore it, for example:

```python
import sqlite3
con = sqlite3.connect(":memory:")
con.executescript(open("fixtures/store.sql").read())
```

Tables (all keys are as in the chapter): `authors(author_id, name, country)`, `books(book_id, title, author_id, category, price, published, pages)`,
`customers(customer_id, name, city, joined)`, `orders(order_id, customer_id, ordered, status)`, `order_items(order_id, book_id, qty, unit_price)`.
`status` is `'shipped'`, `'pending'` or `'cancelled'`. Some cities and pages are NULL. Not every customer has ordered and not every author has a book.

Answer **12 business questions**, one SQL query each, in `solution.py` as `QUERY_1` ... `QUERY_12` (copy `starter.py`).
Each is one `SELECT` (it may start with `WITH`). Use the column names given. Where the statement gives an order, the test compares the rows in that order; where it says "any order", the test sorts them. "Non-cancelled" means `status <> 'cancelled'`.
Round money with `ROUND(x, 2)`. The result must be right for *this* data, but the tests show you what you got and what was expected, so you can debug.

**Q1** `QUERY_1` returns columns `title, price`. Titles and prices of all books that cost **more than 25**. Most expensive first, ties by title.

**Q2** `QUERY_2` returns columns `name`. Names of customers whose city is unknown (NULL), in alphabetical order.

**Q3** `QUERY_3` returns columns `category, books`. How many books are in each category? Largest category first, ties by category name.

**Q4** `QUERY_4` returns columns `name`. Names of authors who have **no books** in the catalogue (any order).

**Q5** `QUERY_5` returns columns `name, revenue`. Revenue per customer, counting only orders whose status is not `'cancelled'`. Revenue is the sum of `qty * unit_price`, rounded to 2 decimals. **Every** customer appears; one without such orders has revenue 0. Highest first, ties by name.

**Q6** `QUERY_6` returns columns `month, revenue`. Revenue per month (`'YYYY-MM'` from the order date), non-cancelled orders only, rounded to 2 decimals, oldest month first.

**Q7** `QUERY_7` returns columns `title, units`. The three best-selling books by total `qty` in non-cancelled orders. Most units first, ties by title.

**Q8** `QUERY_8` returns columns `name, months`. Customers who placed non-cancelled orders in **two or more different months**, with the number of distinct months. Most months first, ties by name.

**Q9** `QUERY_9` returns columns `city, avg_order`. Average **order** value (the total of an order, not of an item row) per city, non-cancelled orders only, rounded to 2 decimals. Show a NULL city as `'Unknown'`. Order by city.

**Q10** `QUERY_10` returns columns `category, title, price`. For each category, its most expensive book (if tied, the lower title). Order by category.

**Q11** `QUERY_11` returns columns `month, revenue, cumulative`. Monthly revenue as in question 6, plus a running total `cumulative` (rounded to 2 decimals), oldest month first.

**Q12** `QUERY_12` returns columns `author, revenue, rank`. Rank the authors by revenue from non-cancelled orders (revenue of all their books' order lines, 2 decimals). `rank` uses `RANK()` with highest revenue = 1. Authors without sales do not appear. Order by rank, then author.

**Example of the style (not one of the questions)**

```sql
SELECT category, ROUND(AVG(price), 2) AS avg_price FROM books GROUP BY category ORDER BY category;
```
