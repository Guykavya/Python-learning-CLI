## Approach

This is a review question: there is no single right query, but there are reliable habits.

## Code

A rewrite keeps the same meaning, with one named step per question:

```sql
WITH first_purchase AS (            -- one row per buyer
  SELECT user_id, min(order_time) AS first_time FROM orders GROUP BY user_id
),
buyer_total AS (                    -- one row per buyer
  SELECT user_id, sum(amount) AS total FROM orders GROUP BY user_id
),
buyer_group AS (                    -- one row per buyer, with channel and month
  SELECT f.user_id, u.channel, date_trunc('month', f.first_time)::DATE AS first_month, t.total
  FROM first_purchase f JOIN users u USING (user_id) JOIN buyer_total t USING (user_id)
  WHERE u.signup_at >= TIMESTAMP '2025-01-01'
)
SELECT channel, first_month, count(*) AS buyers, sum(total) AS revenue
FROM buyer_group GROUP BY channel, first_month ORDER BY revenue DESC
```

(The original also kept only groups whose count exceeds the average number of orders per user; that rule becomes one more CTE.)

## Complexity

Same work as the original, or less: the original joined `orders` to buyers and so repeated each user's `first` row once per order.

## Another way

For checking, also use `EXCEPT` in both directions between the original and the rewrite: both must return zero rows.

## Model answer

The query hides at least four questions: the first order time per user, the channel and month of that first order, the total paid by each buyer, and the threshold "more buyers than the average user has orders". Each should be its own CTE, named by its **grain** (`first_purchase`, `buyer_group`, `buyer_total`), so a reader sees at once what one row means. In the nested query the join of `orders` to the first-purchase table repeats every buyer once per order, so `count(*)` is the number of orders, not the number of buyers: a bug that is easy to see once each step has a stated grain.

While rewriting I would apply: one step per CTE; names that describe the grain; filter early (the `signup_at` condition belongs inside the step that has the column); and no `SELECT *` or unexplained one-letter aliases in the final `SELECT`.

To check, I would run each CTE on its own and compare its row count with what I expect (one row per user). Then I would run the original and the rewrite on a tiny table I can compute by hand, and also compare them with `EXCEPT` in both directions: both results must be empty, or the rewrite is not equivalent. Where they differ, the difference usually points at the fan-out, and the *old* query is the one that was wrong.

**Checklist: your answer should mention**
- [ ] separate questions found (first purchase, channel, total, threshold) and a CTE for each
- [ ] names say the grain
- [ ] filter early / no `SELECT *` at the end / one step per CTE
- [ ] look at each step's row count
- [ ] compare old and new on a tiny table (and/or `EXCEPT`)
