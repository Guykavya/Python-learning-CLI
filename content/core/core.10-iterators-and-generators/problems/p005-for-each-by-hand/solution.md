## Approach

Mirror the hand-written loop: get the iterator once, then repeat `next` inside a `try`. Putting `action(item)` outside the `try` matters: if `action` itself raised `StopIteration` by accident you would not want to hide it.

## Code

```python
def for_each(iterable, action):
    it = iter(iterable)
    count = 0
    while True:
        try:
            item = next(it)
        except StopIteration:
            return count
        action(item)
        count += 1
```

## Complexity

O(n) calls to `action`, O(1) memory.

## Another way

`next(it, sentinel)` with a unique `sentinel = object()` avoids the `try`: `while (item := next(it, sentinel)) is not sentinel:`.
