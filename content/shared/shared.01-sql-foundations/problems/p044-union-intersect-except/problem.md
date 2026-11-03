# UNION, INTERSECT and EXCEPT

Set operations combine the results of two `SELECT`s that have the same number of columns. They treat rows as sets: **duplicates
are removed** (use `UNION ALL` to keep them). `ORDER BY` goes once, at the very end, and sorts the combined result.

```sql
CREATE TABLE newsletter (email TEXT);
CREATE TABLE buyers (email TEXT);
INSERT INTO newsletter VALUES ('a@x'),('b@x'),('c@x'),('b@x');
INSERT INTO buyers VALUES ('b@x'),('d@x'),('d@x');
```

Both tables hold e-mail addresses (a list may contain an address more than once). Write three queries, each returning a single column
`email`, **each address once**, ordered by `email`:

- `QUERY_A`: everyone who is on the newsletter **or** is a buyer (`UNION`).
- `QUERY_B`: people who are on the newsletter **and** are buyers (`INTERSECT`).
- `QUERY_C`: newsletter readers who have **not** bought (`EXCEPT`: newsletter minus buyers).

**Example.** For the data above: `QUERY_A` gives a, b, c, d; `QUERY_B` gives b; `QUERY_C` gives a and c (the order of the two
sides matters for `EXCEPT`).
