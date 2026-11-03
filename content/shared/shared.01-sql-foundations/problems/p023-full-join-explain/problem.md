# Explain: FULL JOIN and how to emulate it

**Scenario.** Pagebound keeps two lists of SKUs (stock codes): what the warehouse holds, and what the website lists.
The ops team asks: "Show me every SKU that appears in **either** list, with its quantity and its web title, so we can spot
books we hold but do not sell, and books we sell but do not hold."

```sql
CREATE TABLE stock   (sku TEXT PRIMARY KEY, qty INTEGER);
CREATE TABLE listing (sku TEXT PRIMARY KEY, title TEXT);
INSERT INTO stock   VALUES ('A1', 5), ('B2', 0), ('C3', 7);
INSERT INTO listing VALUES ('B2', 'Iron Garden'), ('C3', 'Data Basics'), ('D4', 'Night Train');
```

Answer in your own words (150 to 400 words, plus the small result tables you expect):

1. What result would `INNER JOIN` give? Why is it the wrong tool? And a `LEFT JOIN` from `stock` to `listing`?
2. What does a `FULL JOIN` return, and what would the full result be for this data (4 rows)?
3. Write the native `FULL JOIN` query. Which SQLite version added it? What is the problem with selecting only `s.sku`?
4. Before native support, people wrote it as a `UNION` of two `LEFT JOIN`s. Write a correct emulation for older SQLite or for MySQL (which has no FULL JOIN).
   Why is `UNION ALL` plus an anti-join condition in the second half better than plain `UNION`?

Write your answer in `answer.md`, then compare it with the model answer.
