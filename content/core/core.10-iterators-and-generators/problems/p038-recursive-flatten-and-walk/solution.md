## Approach

Both data shapes are recursive: a list can hold lists, and a folder can hold folders. So the code
is recursive too. Each call handles one level. For a nested part it does `yield from` on a
recursive call, which passes every item of the smaller problem up, one by one, without building a
list. The prefix in `walk` carries the path down the levels.

## Code

```python
from collections.abc import Iterator


def flatten(data: list | tuple) -> Iterator[object]:
    for item in data:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


def walk(tree: dict, prefix: str = "") -> Iterator[tuple[str, object]]:
    for name, value in tree.items():
        path = prefix + name
        if isinstance(value, dict):
            yield from walk(value, path + "/")
        else:
            yield path, value
```

## Complexity

O(n) items in total, but each item passes through one generator per level, so the time is
O(n * depth) in the worst case. Memory is O(depth): one paused generator per level, never a full list.
Very deep data (about 1000 levels) hits Python's recursion limit.

## Another way

Without recursion, keep your own stack of iterators: start with `[iter(data)]`, take `next` from
the top one; if the item is a list, push `iter(item)`; if the top iterator is finished, pop it.
That has no depth limit and shows what the recursive version does for you.
