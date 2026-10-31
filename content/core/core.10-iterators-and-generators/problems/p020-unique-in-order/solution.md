## Approach

Keep a set `seen` of everything already given out. For each item, work out its marker: the
item itself, or `key(item)` when a key function is given. If the marker is new, remember it
and yield the original item. If not, skip it.

The set is the only thing that grows. The input is never stored, so this works on a stream.

## Code

```python
def unique(iterable, key=None):
    seen = set()
    for item in iterable:
        marker = item if key is None else key(item)
        if marker not in seen:
            seen.add(marker)
            yield item
```

## Complexity

O(n) time (set lookups are O(1) on average). Memory is O(number of different markers).

## Another way

`list(dict.fromkeys(items))` keeps order and removes repeats in one line, but it builds the
whole result at once, so it is not lazy and it has no `key` option.
