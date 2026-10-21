## Hint 1

How can one key make marks go high-to-low but names go A-to-Z? What happens to the order of numbers when you negate them?

## Hint 2

`key=lambda r: (-r[1], r[0].lower())` sorts the tuples. Then take the names.

## Hint 3

```
ranked = sorted(records, key=lambda r: (-r[1], r[0].lower()))
names = [name for name, marks in ranked]
return names if top is None else names[:top]
```
