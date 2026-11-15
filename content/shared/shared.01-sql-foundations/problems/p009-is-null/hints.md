## Hint 1

What does `pages = NULL` evaluate to for a row whose pages is NULL? Is that true, false or something else?
Which operator is made for this?

## Hint 2

```
A: SELECT title FROM books WHERE pages <the NULL test>
B: SELECT title FROM books WHERE pages <the opposite test>
```

A and B together should cover every book exactly once.
