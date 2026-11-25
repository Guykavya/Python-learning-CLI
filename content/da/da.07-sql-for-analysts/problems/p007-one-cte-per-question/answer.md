## Model answer

The query hides at least four questions: the first order time per user, the channel and month of that first order, the total
paid by each buyer, and the threshold "more buyers than the average number of orders per user". Each should be its own CTE,
named by its **grain** (`first_purchase`, `buyer_group`, `buyer_total`), so a reader sees at once what one row means. In the
nested query the join of `orders` to the first-purchase table repeats every buyer once per order, so `count(*)` is the number
of orders, not the number of buyers: a bug that is easy to see once each step has a stated grain.

While rewriting I would apply: one step per CTE; names that describe the grain; filter early (the `signup_at` condition
belongs inside the step that owns the column); and no `SELECT *` or one-letter aliases in the final `SELECT`.

To check, I would run each CTE on its own and compare its row count with what I expect (one row per user). Then I would run
the original and the rewrite on a tiny table I can compute by hand, and also compare them with `EXCEPT` in both directions: both
results must be empty, or the rewrite is not equivalent. Where they differ, the difference usually points at the fan-out, and
the *old* query is the one that was wrong.

**Checklist: your answer should mention**
- [ ] separate questions found (first purchase, channel, total, threshold) and a CTE for each
- [ ] names say the grain
- [ ] filter early / no `SELECT *` at the end / one step per CTE
- [ ] look at each step's row count
- [ ] compare old and new on a tiny table (and/or `EXCEPT`)
