## Hint 1

First get the whole list in the right order, with a tie-break. Then ask: how many rows must I skip
to get past page 1, and how many do I keep?

## Hint 2

```
SELECT title FROM books
ORDER BY <price>, <title>
LIMIT <page size> OFFSET <(page - 1) * page size>
```

Dataset A has two books at 9.99 and two at 18.00: ties matter.
