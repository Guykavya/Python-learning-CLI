## Hint 1

Read the query from the inside out and list every `FROM (SELECT ...)`. Each subquery answers one question; what is one row in each? Then reread the chapter's rules of thumb (3.2): name by grain, keep each step small, look at each step's row count.

## Hint 2

```text
paragraph 1: the separate questions (first order per user; channel of the buyer; total per buyer; the average-orders threshold) and a name for each CTE that says its grain
paragraph 2: rules: one step per CTE, names say the grain, filter early, no SELECT * at the end, say why a join is safe
paragraph 3: checking: run each CTE alone and count rows; compare original vs rewrite with EXCEPT both ways; try a tiny table
```
