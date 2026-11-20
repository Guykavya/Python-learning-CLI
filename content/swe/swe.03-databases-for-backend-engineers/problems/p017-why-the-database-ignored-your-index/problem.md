# Why the database ignored your index

A colleague added `CREATE INDEX idx_users_active ON users(is_active)` because the query

```sql
SELECT * FROM users WHERE is_active = 1;
```

was slow. The table has 1,000,000 rows and **90% of them** have `is_active = 1`. After the index, the plan still shows `SCAN users` and the query is no faster. (And in another query, `WHERE is_active = 0`, the index is used.)

In `answer.md` (10 to 14 sentences), explain (chapter section 5.8):

1. What is **selectivity**, and what is the selectivity of `is_active = 1` here?
2. Why can reading 900,000 rows **through** an index be slower than scanning the table?
3. What does the planner use to choose, and what does `ANALYZE` change?
4. Why is the index used for `is_active = 0`?
5. What would be a **better index** (or query) for a page that shows active users? Give one example.
