- Returning `[31, 25, 40]` for one index. `itemgetter` with one argument does not make a tuple.
- Writing `(getter(row))` for the one-item case. Brackets alone are not a tuple; you need the comma: `(value,)`.
- Returning `map(...)` directly. A map object is lazy and is not equal to a list.
- In `get_path`, using `if not value: return default`. Real values such as `False`, `0` or `""`
  are then treated as missing.
- Catching only `KeyError`. Lists raise `IndexError`, and indexing an `int` raises `TypeError`.
- Catching every exception with `except Exception:`. That also hides real bugs.
