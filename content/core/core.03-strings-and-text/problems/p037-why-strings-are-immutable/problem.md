# Why strings are immutable

A classmate writes:

```python
name = "asha"
name[0] = "A"
```

and gets `TypeError: 'str' object does not support item assignment`. Later they write a program that builds a 50,000-line report with `report += line + "\n"` inside a loop, and a senior developer tells them to use `"".join(...)` instead.

Explain in your own words, in `answer.md`:

1. What "immutable" means for a Python string, and how you *do* produce a changed version of `name`.
2. Why `name.upper()` on its own line does not change `name`.
3. At least two benefits of strings being immutable.
4. Why building a long string with repeated `+=` can be slow, and why `join` is faster.
5. Why `+=` sometimes seems fast in CPython anyway, and why you should not rely on that.

Use small examples. Aim for an explanation a classmate could follow.
