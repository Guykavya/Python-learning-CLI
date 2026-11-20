## Approach

The model answer is in `answer.md`. Remember: an index is not a magic speed-up, it is a bet that the query touches **few** rows.

You can check on your own machine: create a table with 90% ones, add the index, and compare `EXPLAIN QUERY PLAN` for `is_active = 1` and `is_active = 0`, before and after `ANALYZE`.

## Complexity

Not applicable.

## Another way

Rewrite the query: fetch the **inactive** users and subtract, or fetch only the page you need with `LIMIT`. Often the best fix is changing what the page asks for.

## Why it matters

Adding indexes without reading plans costs write speed and disk space for nothing. The plan tells whether the index was used; selectivity tells whether it could be.
