## Approach

Keep two things in your head: the running total, and whether `qs` has loaded its rows.

```text
1: 0
2: 0
3: 1
4: 2
5: 2
6: 2
7: 3
8: 3
```

- **1.** `filter()` only builds a recipe: 0 queries.
- **2.** `order_by()` and the slice `[:2]` build a *second*, new QuerySet (`top`). A slice of an unevaluated QuerySet becomes `LIMIT 2` and still runs nothing: 0 added.
- **3.** `count()` asks the database `SELECT COUNT(*) ...`. The rows of `qs` are **not** loaded, so this is query number 1 and the cache stays empty.
- **4.** The first loop over `qs` runs the full `SELECT` and stores the rows in the QuerySet: query 2.
- **5.** The second loop reads the stored rows: no query.
- **6.** `len(qs)` also reads the stored rows: no query.
- **7.** `Item.objects.filter(quantity=0)` is a different QuerySet with its own empty cache. `exists()` sends `SELECT 1 ... LIMIT 1`: query 3.
- **8.** `qs.first()`: `qs` is already loaded, and `first()` takes the first row of the cache instead of asking the database again. Total stays 3.

Real output of the program, run with Django 6.1.3.

The practical rules: use `count()` or `exists()` when you only need a number or a yes/no and nothing is loaded; once you need the rows anyway, load them once (`list(qs)`) and reuse them. Do not call `len()` first just to count (it loads everything), and do not call `count()` after you have loaded the rows (it is free then, but `len()` says the same).

## Complexity

Not applicable; this is a reading exercise.

## Another way

Print `len(ctx)` is only one way to see queries. `print(qs.query)` shows the SQL of one QuerySet without running it, and `ctx.captured_queries` lists each statement. In tests you use `assertNumQueries(n)` (section 14) or this same context manager to freeze the count of a page.
