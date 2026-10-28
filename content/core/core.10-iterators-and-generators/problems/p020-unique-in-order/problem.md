# Remove repeats from a stream, keeping order

A sign-up form sends e-mail addresses one by one. Some people sign up twice, sometimes with
different capital letters. You want each person once, in the order they first appeared.

Write a **generator function** `unique(iterable, key=None)` in `solution.py`.

- It yields each item the **first** time it is seen and skips later repeats.
- The order of first appearance is kept.
- If `key` is given, it is a function. Two items are "the same" when `key(item)` is equal.
  The item that is yielded is still the **original** item, not `key(item)`.
- It must be lazy: it works on an endless stream and yields an item as soon as it is new.

You can assume the items (or their keys) are hashable.

**Example**

```python
list(unique([3, 1, 3, 2, 1]))                         # [3, 1, 2]
"".join(unique("banana"))                             # 'ban'
list(unique(["Ann@x.in", "ann@x.in", "Bob@y.in"], key=str.lower))
# ['Ann@x.in', 'Bob@y.in']
```
