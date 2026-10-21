# Return a bool, do not print it

Write `is_even(n)` that returns `True` when the integer `n` is even and `False` when it is odd.

It must **return** a real bool (`True` or `False`), not the strings `"True"`/`"even"`,
and must not print anything.

**Examples**

```python
is_even(4)     # True
is_even(7)     # False
is_even(0)     # True
is_even(-3)    # False
```

Because it returns a bool, callers can use it directly in conditions:
`if is_even(count): ...`
