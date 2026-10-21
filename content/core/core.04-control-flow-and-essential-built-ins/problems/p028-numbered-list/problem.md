# Numbered list with enumerate

Read one line of items separated by commas, such as `milk, bread ,eggs`. Print each item,
stripped of spaces, numbered from 1:

```
1. milk
2. bread
3. eggs
Total: 3 items
```

If the line is blank, print only `(no items)`. Use `Total: 1 item` for a single item.

**Rule for this problem:** use `enumerate` with `start=1`. Do not use `range` at all. The
tests check this.
