# Rebuild chain, zip, enumerate and islice

The best way to understand a tool is to build it. Write four generator functions in `solution.py`
that behave **exactly** like the real ones. Do not import `itertools` and do not call the
built-in `zip` or `enumerate` in your solution; the tests compare your versions with the real ones.

1. `my_chain(*iterables)`: all items of the first iterable, then all of the second, and so on.
2. `my_enumerate(iterable, start=0)`: pairs `(index, item)`, the index counting from `start`.
3. `my_zip(*iterables)`: tuples of one item from each iterable. Stop as soon as **any** of them
   runs out. With no iterables, yield nothing.
4. `my_islice(iterable, start, stop)`: the items with positions `start, start + 1, ..., stop - 1`.
   If `stop` is `None`, there is no end. It must **not** take any item after position `stop - 1`
   from the iterable.

All four must be lazy: they must work on infinite inputs such as `itertools.count()`.

**Examples**

```python
list(my_chain([1, 2], "ab", []))        # [1, 2, "a", "b"]
list(my_enumerate("xy", start=1))       # [(1, "x"), (2, "y")]
list(my_zip([1, 2, 3], "ab"))           # [(1, "a"), (2, "b")]
list(my_islice("abcdefg", 2, 5))        # ["c", "d", "e"]
```

**An internal detail to copy.** The real `zip` asks the iterables for items from left to right. In
`zip(a, b)`, when `b` runs out, one item has **already** been taken from `a` and is lost:

```python
a = iter([1, 2, 3])
b = iter(["x"])
list(zip(a, b))    # [(1, "x")]
next(a)            # 3   (2 was taken from a, then b ran out)
```

Your `my_zip` must lose exactly the same item. The natural implementation does this.
