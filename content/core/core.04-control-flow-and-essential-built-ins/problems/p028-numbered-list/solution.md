## Approach

Split on commas, then let `enumerate` count from 1 while the loop gives the items.

## Code

```python
line = input()
if not line.strip():
    print("(no items)")
else:
    items = line.split(",")
    for number, item in enumerate(items, start=1):
        print(f"{number}. {item.strip()}")
    word = "item" if len(items) == 1 else "items"
    print(f"Total: {len(items)} {word}")
```

## Why `enumerate` instead of `range(len(items))`

`enumerate` hands you the item itself, so there is no `items[i]` and no `+ 1` for human
numbering. Fewer moving parts, fewer off-by-one chances.

## Why check for a blank line first

`"".split(",")` gives `[""]`, one empty item, so the loop would print `1. `.
