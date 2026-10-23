## Walkthrough

1. `double(4)` is `8`.
2. `double("ab")`: a string times 2 repeats it, `abab`. The hint said `int` and Python never looked.
3. `double([1, 2])`: a list times 2 repeats it, `[1, 2, 1, 2]`.
4. `double(2.5)` is `5.0`. A float is not an `int`, but the body works anyway.
5. `shout("hey")` is `HEY`.
6. `shout(5)`: `5` has no `.upper()`, so `AttributeError` is raised **inside the body**, not because of the hint. The `except` prints `AttributeError`.
7. `double.__annotations__` is `{'n': int, 'return': int}`, so the comparison is `True`.

The program was checked by really running it. mypy 2.4.0 would flag lines 10, 11, 12 and 15 of this file (all four `[arg-type]`); Python flags none of them by itself.

## The exact output

```text
8
abab
[1, 2, 1, 2]
5.0
HEY
AttributeError
True
```
