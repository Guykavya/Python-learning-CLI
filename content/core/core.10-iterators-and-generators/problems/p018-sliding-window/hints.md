## Hint 1

Keep the last `k` items you have seen. When a new item arrives, what goes in, and what falls out?

## Hint 2

A tuple can grow with `window + (item,)` and lose its first item with `window[1:]`.
When is the window "full" and ready to yield?

## Hint 3

```
window = ()
for item in iterable:
    window = window + (item,)
    if len(window) > k: drop the first item
    if len(window) == k: yield window
```
