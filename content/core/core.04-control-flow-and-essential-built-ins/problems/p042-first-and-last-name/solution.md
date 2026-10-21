## Approach

`min` and `max` with `key=str.lower` compare case-insensitively and return the original
spelling. `key=len` gives the longest.

## Code

```python
names = input().split()
if not names:
    print("No names")
else:
    print(f"First: {min(names, key=str.lower)}")
    print(f"Last: {max(names, key=str.lower)}")
    print(f"Longest: {max(names, key=len)}")
```

## Why `str.lower` and not `lower`

`key` needs a function that takes one item. `str.lower` is the `lower` method taken from the
`str` type, so `str.lower("Zoya")` is `"zoya"`. `"Zoya".lower` would be bound to one
particular string.

## Another way

Without key functions you would loop, keep the best name so far and compare `name.lower()`
with `best.lower()`. It is longer and easy to get wrong on ties.
