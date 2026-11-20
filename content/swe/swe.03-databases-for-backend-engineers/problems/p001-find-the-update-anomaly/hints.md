## Hint 1

You need, for each key, the list of different values seen so far. Which structure maps a key to such a list?

## Hint 2

`dict.setdefault(key, [])` gives you the list for a key, creating it when needed. Add a value only if it is not in the list yet (keeps the first-seen order).

## Hint 3

```text
seen = {}
for row in rows: values = seen.setdefault(row[key], []); append row[field] if not already there
return only the entries of seen with len(values) > 1
```
