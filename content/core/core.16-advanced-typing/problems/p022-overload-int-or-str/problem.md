# overload: one name, different result types

A function that returns `int | str` forces every caller to check the result. When the result type
depends on the argument type, `@overload` states the exact link. You write several signatures
(each body is just `...`) and then **one** real implementation.

Write in `solution.py`:

1. `double(x)`:
   - given an `int` it returns `x * 2` (an `int`),
   - given a `str` it returns the text repeated twice (`"ab"` becomes `"abab"`),
   - given anything else it raises `TypeError`.

   Overloads: `double(x: int) -> int` and `double(x: str) -> str`.

2. `to_number(text, as_float=False)`:
   - with `as_float=True` it returns `float(text)`,
   - otherwise it returns `int(text)`.

   Overloads: `to_number(text: str, as_float: Literal[True]) -> float` and
   `to_number(text: str, as_float: Literal[False] = False) -> int`.

   (A `Literal` type lets the checker pick the overload from the **value** of the argument.)

The implementation signature itself is not an overload. Give it a wide hint, for example
`def double(x: int | str) -> int | str:`.

The tests read your overloads with `typing.get_overloads(...)` and check their annotations, then
run the functions.

**Example**

```python
double(21)             # 42
double("ab")           # "abab"
double(2.5)            # TypeError
to_number("7")         # 7
to_number("7", True)   # 7.0
```

**Remember**: `@overload` changes nothing at run time. Only the last, undecorated definition runs.
Its signature is checked against all the overloads.
