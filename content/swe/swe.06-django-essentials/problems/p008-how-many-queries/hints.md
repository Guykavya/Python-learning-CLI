## Hint 1

Keep a running total and a note: "has `qs` loaded its rows yet?" Start with 0 queries and "not loaded". Which lines only *build* a QuerySet (filter, order, slice)? Those add nothing. Then find the first line that really needs rows or a number from the database.

## Hint 2

`count()` on a QuerySet that is **not** loaded sends `SELECT COUNT(*)` and does not load the rows. Looping (or `list()`) sends the full `SELECT` and fills the cache. After that, looping again, `len()`, and methods that can read the cache (`count()`, `first()`, `exists()`) cost nothing. A **different** QuerySet object (line 7) has its own, empty cache.

## Hint 3

```text
1  define qs                     no SQL                 total 0
2  slice top = qs.order_by()[:2] still no SQL           total 0
3  qs.count()                    SELECT COUNT(*)        total 1   (qs still not loaded)
4  loop over qs                  SELECT ...             total 2   (qs loaded now)
5  loop again                    cache                  total 2
6  len(qs)                       cache                  total 2
7  new QuerySet .exists()        SELECT 1 ... LIMIT 1   total 3
8  qs.first()                    qs is loaded: from cache  total 3
```
