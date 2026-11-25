# Three counts in SQL

Chapter section 10.1. The three counts of section 5 exist in SQL too, and they differ exactly as in pandas:

| SQL | counts | pandas |
|---|---|---|
| `COUNT(*)` | rows | `len(df)` |
| `COUNT(col)` | rows where `col` is **not NULL** | `df[col].count()` |
| `COUNT(DISTINCT col)` | different non-NULL values | `df[col].nunique()` |

The table `payments` has one row per payment:

```text
payments(payment_id INTEGER, customer_id INTEGER, method TEXT, amount INTEGER, paid_at TEXT)
```

`method` is `NULL` when the payment method was not recorded. `customer_id` may also be `NULL`. `paid_at` is text in the
format `YYYY-MM-DD HH:MM:SS`.

In `solution.py`, define a text `QUERY` (one `SELECT` statement) that returns **one row with three columns, named and
in this order**:

1. `rows`: the number of payment rows
2. `with_method`: the number of payments that have a method recorded
3. `distinct_customers`: the number of different customers who paid (a `NULL` customer is not a customer)

## Example

```sql
CREATE TABLE payments (payment_id INTEGER, customer_id INTEGER, method TEXT, amount INTEGER, paid_at TEXT);
INSERT INTO payments VALUES
  (1, 10, 'upi',  500, '2025-02-01 10:00:00'),
  (2, 10, NULL,   300, '2025-02-02 10:00:00'),
  (3, 11, 'card', 200, '2025-02-03 10:00:00');
```

With these three rows the result is one row: `rows = 3`, `with_method = 2`, `distinct_customers = 2`.
