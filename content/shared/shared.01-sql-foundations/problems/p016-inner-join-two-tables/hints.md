## Hint 1

Which column in `books` links to which column in `authors`? What must be true about two rows for them to belong together? After joining, both tables have a column called `name` or `author_id`: how do you say which one you mean?

## Hint 2

```
SELECT b.title, a.name AS author
FROM books AS b
JOIN authors AS a ON <a.key equals b.key>
```

Does author 5 (no books) appear? Should it?
