# Fenwick: range sum

Extend the Fenwick tree of p013 into a complete range-sum structure (chapter section 10, "The class"). Public interface **0-indexed and half-open**.

- `Fenwick(n, a=None)`: `n` zeros, or the values of the list `a` if given, built in **`O(n)`**;
- `add(i, v)`: `a[i] += v`;  `prefix(r)`: sum of `a[0:r]`;
- `range_sum(l, r)`: sum of `a[l:r]`;
- `get(i)`: the current `a[i]`;  `set(i, v)`: `a[i] = v`.

## Example

```python
>>> fw = Fenwick(8, [5, 3, 8, 6, 2, 7, 4, 1])
>>> fw.t[1:]
[5, 8, 8, 22, 2, 9, 4, 36]
>>> fw.range_sum(2, 7), fw.range_sum(3, 3), fw.get(5)
(27, 0, 7)
>>> fw.set(3, 100)
>>> fw.range_sum(2, 7), fw.get(3)
(121, 100)
```

## Constraints

- `n` up to 10**6 for the build (calling `add` `n` times would be `O(n log n)`; the tests time the build alone), up to 2 * 10**5 operations.

## Think about

1. Why is `range_sum(l, r) = prefix(r) - prefix(l)` and not `prefix(r) - prefix(l - 1)` here?
2. A Fenwick tree only knows how to **add**. How do you **set** a value?
3. How can every cell be filled in one pass, with each finished cell added to exactly one other cell?
