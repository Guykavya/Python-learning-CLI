## Model answer

1. **Gain and cost.** The stored total makes the page read **one number per order** instead of summing all its lines, so reads become cheap and need no join. The price is on the **write** side: every time a line is added, changed or removed, the total must be updated as well, and the table is a little bigger. It pays off when reads are far more frequent than writes.
2. **New bug.** The data can now **contradict itself** (an update anomaly): a line is changed in one place (an admin script, a bug fix) and the total is not, so the page shows 800.00 while the lines add up to 850.00. Before, that was impossible.
3. **Keeping it correct.** (a) **One place writes it**: all changes to lines go through one function (or a database trigger), never scattered `UPDATE`s. (b) Do the line change and the total update in **one transaction**, so a crash cannot leave them half done. (Also: constraints such as `CHECK (total_paise >= 0)`, and tests.)
4. **Reconciliation query.**
   ```sql
   SELECT o.id, o.total_paise, COALESCE(SUM(l.qty * l.price_paise), 0) AS real_total
   FROM orders o LEFT JOIN order_lines l ON l.order_id = o.id
   GROUP BY o.id
   HAVING o.total_paise <> COALESCE(SUM(l.qty * l.price_paise), 0);
   ```
   Run it regularly (or in a test) and alert on any row.
5. **When not to store it.** When the sum is cheap (few lines per order, an index on `order_lines(order_id)`), when writes are frequent, or when correctness matters more than speed. First measure and add the index; denormalise only when the numbers say so.

**Checklist: your answer should mention**
- [ ] reads become cheaper, **writes cost more**
- [ ] the data can now **disagree** with itself
- [ ] **one place** writes the total, and a **transaction** (or trigger)
- [ ] a **reconciliation query** comparing stored and computed totals
- [ ] when **not** to do it (measure first, an index may be enough)
