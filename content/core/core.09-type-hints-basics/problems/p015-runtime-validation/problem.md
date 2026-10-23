# Hints do not validate: check at runtime

A hint does not stop a wrong value. When data comes from outside, you must check it yourself.
Write two annotated functions in `solution.py`.

1. `set_age(age: int) -> int` returns `age` if it is acceptable and otherwise raises:
   - `TypeError` with a message containing `"int"` if `age` is not an `int`. A `bool` (`True` or
     `False`) also counts as **not** acceptable here, even though Python treats it as an `int`.
   - `ValueError` with a message containing `"between"` if `age` is below `0` or above `150`.
     (`0` and `150` are fine.)
2. `require_str_list(values: object) -> list[str]` returns `values` unchanged if it is a list
   in which every item is a `str`, and otherwise raises:
   - `TypeError` with a message containing `"list"` if `values` is not a list;
   - `TypeError` with a message containing `"str"` if some item is not a `str`.

Note the hint `object` in the second function: it says "anything may arrive here", because the
function's whole job is to inspect an unknown value.

**Examples**

```python
set_age(21)                      # 21
set_age("21")                    # raises TypeError("age must be an int")
set_age(True)                    # raises TypeError("age must be an int")
set_age(200)                     # raises ValueError("age must be between 0 and 150")
require_str_list(["a", "b"])     # ["a", "b"]
require_str_list(("a", "b"))     # raises TypeError("expected a list")
require_str_list(["a", 1])       # raises TypeError("every item must be a str")
```
