# Narrowing with isinstance

A value of type `int | str | None` could be any of three things. A type checker lets you use it
only in ways that are safe for **all** of them, until an `isinstance` (or `is None`) test
**narrows** it. Inside the `if` the checker knows the exact type.

Write four functions in `solution.py`, with these exact hints, and use `isinstance` in each one:

| Function | Hints | What it does |
|---|---|---|
| `to_int(value)` | `value: int \| str \| None` -> `int` | `None` gives `0`, a `str` is converted with `int(...)` (text that is not a number raises `ValueError`, even `""`), an `int` is returned as it is |
| `describe(value)` | `value: int \| str \| list[int]` -> `str` | `"int 5"` for `5`, `"str 'ab'"` for `"ab"` (use `repr`), `"list of 3"` for a list with 3 items |
| `total_length(items)` | `items: list[str \| list[str]]` -> `int` | a `str` counts its length, a nested list counts the **sum of its items' lengths** |
| `first_text(values)` | `values: list[int \| str]` -> `str \| None` | the first `str` in the list, or `None` if there is none |

The tests read the hints with `get_type_hints` (the order of the union members does not matter,
and `Optional[...]` is accepted), check by reading your source with `ast` that each function
really calls `isinstance`, and run the functions.

**Example**

```python
to_int("12")                      # 12
to_int(None)                      # 0
describe([1, 2, 3])               # "list of 3"
total_length(["ab", ["c", "de"]]) # 5   (2 + 1 + 2)
first_text([1, 2, "x", "y"])      # "x"
```

**Remember**: a list can never be narrowed by `isinstance(v, list[int])`. Test `isinstance(v, list)`
and let the declared hint tell the checker what is inside.
