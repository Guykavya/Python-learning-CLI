# One CTE per question

Chapter sections 3.1 and 3.2. A teammate sends you this query. It runs and the numbers look plausible, but nobody wants to
maintain it:

```sql
SELECT c, m, n, rev, rev * 1.0 / n AS rev_per_buyer
FROM (
  SELECT u2.channel AS c, date_trunc('month', f.t) AS m, count(*) AS n, sum(o2.amount) AS rev
  FROM (SELECT user_id, min(order_time) AS t FROM orders GROUP BY user_id) f
  JOIN users u2 ON u2.user_id = f.user_id
  JOIN orders o2 ON o2.user_id = f.user_id
  WHERE u2.signup_at >= TIMESTAMP '2025-01-01'
  GROUP BY u2.channel, date_trunc('month', f.t)
) x
WHERE n > (SELECT avg(k) FROM (SELECT count(*) AS k FROM orders GROUP BY user_id) y)
ORDER BY rev DESC
```

In `answer.md`, in about 150 to 250 words, explain how you would **rewrite and check** it:

1. What are the separate questions hidden inside (name at least three), and what would each CTE be called and what is its grain?
2. Which two or three habits from the chapter's CTE rules of thumb would you apply while rewriting (for example about naming,
   filtering, the final `SELECT`)?
3. How do you check the rewrite gives the **same** answer as the original, and that each step is right on its own?

## Example

A start: "The query mixes four questions: who bought first and when, what channel they belong to, how much each buyer paid, and
which groups are large enough to show. I would give each its own CTE, named by grain: `first_purchase_per_user`, ..."
