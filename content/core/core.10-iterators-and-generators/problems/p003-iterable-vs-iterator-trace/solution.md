## Approach

`nums` is a list: iterable, but it holds the data and no position. `it = iter(nums)` is an iterator: it holds a position. `next(it)` moves the position; `list(it)` moves it to the end; the second `list(it)` finds nothing left. The list itself is untouched, so it can be iterated again. Every `iter(nums)` creates a new iterator object, so two of them are never the same object. `iter(it)` returns `it` itself.

## Output

```text
10
[20, 30]
[]
[10, 20, 30]
[10, 20, 30]
False
True
```

## Complexity

O(n).

## Another way

Run `print(iter(nums))` to see `<list_iterator object at 0x...>` (the address is machine-specific): the iterator is a separate small object that points into the list.
