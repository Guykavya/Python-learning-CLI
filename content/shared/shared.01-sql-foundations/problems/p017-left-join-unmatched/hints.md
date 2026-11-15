## Hint 1

Which table must keep all its rows: authors or books? So which table goes on the left of `LEFT JOIN`? What will SQL put in the book columns for an author with no match?

## Hint 2

```
SELECT a.name AS author, b.title
FROM authors AS a
LEFT JOIN books AS b ON <match on author_id>
```
