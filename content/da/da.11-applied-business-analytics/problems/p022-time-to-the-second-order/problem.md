# Time to the second order

Chapter section 4.6. A retention table needs many cohorts. A simpler view: **how long until a customer buys again?** Write `days_to_second(orders)` for a table with `customer_id` and `order_date`:

- for each customer with **at least two orders**, the number of days between the **first and the second** order (the second earliest date; two orders on the same day give 0);
- one-order customers are **not** in the result but are **counted**;
- return a dict `{"days": Series, "one_order": int, "median": float}` where `days` is indexed by `customer_id` (sorted by id), values are ints, `one_order` is the number of customers with exactly one order, and `median` is the median of `days` (`NaN` if nobody has two orders).

The median is only about the customers who **did** reorder: say so when you report it (the chapter's warning).

## Example

Customer a orders on days 0, 30, 100; b on day 5 only; c on day 7 twice. Then `days` is `a: 30, c: 0`, `one_order` is 1 and the median is 15.0.
