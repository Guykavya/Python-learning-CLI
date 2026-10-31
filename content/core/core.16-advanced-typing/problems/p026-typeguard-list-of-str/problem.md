# TypeGuard: is this a list of str?

`isinstance(x, list)` tells the checker that `x` is a list, but not what is **inside**. If you
get a `list[object]` (say, from parsed JSON) and want to use it as `list[str]`, you write a
function that checks every item and tell the checker its result with `TypeGuard`.

In `solution.py` write:

1. `is_str_list(value)` with hints `value: list[object]` -> `TypeGuard[list[str]]`.
   It returns `True` when **every** item is a `str` (an empty list gives `True`).
2. `is_int_dict(value)` with hints `value: dict[str, object]` -> `TypeGuard[dict[str, int]]`.
   It returns `True` when every **value** is an `int`. A `bool` does **not** count as an int here
   (`{"a": True}` gives `False`).
3. `join_if_strings(items)` with hints `items: list[object]` -> `str`. If `is_str_list(items)` is
   true it returns `", ".join(items)`, otherwise `""`. (This function is where the guard pays
   off: `", ".join(items)` is only accepted by the checker because the guard narrowed `items`.)
4. `sum_counts(data)` with hints `data: dict[str, object]` -> `int`. If `is_int_dict(data)` is
   true it returns the sum of the values, otherwise it raises `ValueError`.

The tests read the hints (the return hint must be a `TypeGuard`), and run the functions.

**Example**

```python
is_str_list(["a", "b"])        # True
is_str_list(["a", 1])          # False
is_str_list([])                # True
is_int_dict({"a": 1, "b": 2})  # True
is_int_dict({"a": True})       # False
join_if_strings(["x", "y"])    # "x, y"
join_if_strings(["x", 1])      # ""
sum_counts({"a": 1, "b": 2})   # 3
```

**Remember**: at run time a `TypeGuard` function is just a function that returns a `bool`. The
checker **trusts** you: if your function says `True` for a list with a number in it, the checker
will not notice.
