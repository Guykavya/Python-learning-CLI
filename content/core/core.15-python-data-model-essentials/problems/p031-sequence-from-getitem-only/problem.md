# A sequence from `__getitem__` alone

Before `__iter__` existed, Python iterated with a trick: if an object has no `__iter__`, `iter(obj)`
builds an iterator that calls `obj[0]`, `obj[1]`, `obj[2]`, ... and stops when `IndexError` is
raised. The trick still works today. That means a class with **only `__getitem__`** already works in
`for` loops, `list()`, `in`, `sum()` and `zip()`.

Write two classes in `solution.py`:

**`Multiples(step, count)`** defines **only** `__init__` and `__getitem__`. `m[i]` is
`step * (i + 1)` for `0 <= i < count`. Any other integer (including negatives) raises `IndexError`.
A non-integer raises `TypeError`. Do **not** define `__iter__` or `__len__`; the tests check this.

**`Backwards(seq)`** wraps any sequence (a list, a string, another `Backwards`) and reads it from
the end: `b[0]` is the last item. It defines `__init__`, `__len__` and `__getitem__` only. With these
two methods `reversed(b)` works as well. Same index rules: only `0 <= i < len`, otherwise
`IndexError`; non-integers raise `TypeError`.

**Example**

```python
list(Multiples(3, 4))            # [3, 6, 9, 12]
12 in Multiples(3, 4)            # True
len(Multiples(3, 4))             # TypeError: object of type 'Multiples' has no len()
b = Backwards([1, 2, 3])
list(b)                          # [3, 2, 1]
list(reversed(b))                # [1, 2, 3]
```
