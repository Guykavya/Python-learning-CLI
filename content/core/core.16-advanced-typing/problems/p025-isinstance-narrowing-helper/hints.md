## Hint 1

For each function, list the possible types of the argument. What question (`isinstance` with which class, or `is None`) separates them one by one? After you handle one case and `return`, which cases are left?

## Hint 2

Handle the cases in order and return early; the last case needs no test because only one type is left. `None` is tested with `is None`, not `isinstance`. For `total_length`, the loop variable is `str | list[str]`: test `isinstance(item, str)` and the `else` branch is the list.

## Hint 3

```
to_int:       if value is None: return 0
              if isinstance(value, str): return int(value)
              return value
describe:     int -> f"int {value}" ; str -> f"str {value!r}" ; else list -> f"list of {len(value)}"
total_length: for item in items: str -> len(item) ; else -> sum(len(s) for s in item)
first_text:   for v in values: if isinstance(v, str): return v   ; return None
```
