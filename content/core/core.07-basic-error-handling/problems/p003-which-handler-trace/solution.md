## Walkthrough

1. `data["b"]` raises `KeyError`; the first clause matches.
2. `data["a"][5]` raises `IndexError`. It is not a `KeyError`, but it **is** a `LookupError`, so
   the second clause runs.
3. `10 % 0` raises `ZeroDivisionError`, a child of `ArithmeticError`.
4. `int("ten")` raises `ValueError`, matched by the tuple; `type(e).__name__` is `ValueError`.
5. `len(42)` raises `TypeError`, also in the tuple.
6. `data["a"][-1]` is `2`: no exception, so "no error" is printed.
7. `[3, 1].index(2)` raises `ValueError` (not a `LookupError`!), caught by the tuple.
8. `undefined_name` raises `NameError`, which matches no clause. It propagates out of `attempt`
   and the outer `try` catches it.

## The exact output

```text
1 -> KeyError handler
2 -> LookupError handler
3 -> ArithmeticError handler
4 -> ValueError in the tuple handler
5 -> TypeError in the tuple handler
6 -> no error
7 -> ValueError in the tuple handler
8 escaped as NameError
end
```
