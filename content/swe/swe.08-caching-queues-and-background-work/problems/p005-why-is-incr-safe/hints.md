## Hint 1

Draw two columns, A and B, and four rows of time. Where must B's `GET` happen so that A's `SET` is wasted?

## Hint 2

For question 2, ask: can anything happen *between* Redis reading the old value and writing the new one inside `INCR`? Recall the chapter's sentence about how Redis runs commands. For question 5, look at `hit_safe` in section 7.2.
