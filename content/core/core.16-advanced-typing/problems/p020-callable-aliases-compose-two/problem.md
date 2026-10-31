# Callable aliases and compose_two

Write these in `solution.py`.

**Two aliases** (module-level names, defined with a plain assignment or the `type` statement):

- `IntTransform` means "a function from `int` to `int`": `Callable[[int], int]`.
- `IntPredicate` means "a function from `int` to `bool`": `Callable[[int], bool]`.

**Functions**

1. `count_matching(items: list[int], pred: IntPredicate) -> int` counts the items for which
   `pred(item)` is true.
2. `apply_all(x: int, steps: list[IntTransform]) -> int` passes `x` through every step in order
   and returns the final value (no steps: returns `x`).
3. `compose_two(f, g)` returns a **new function** that first calls `f` and then calls `g` on the
   result: `compose_two(f, g)(x) == g(f(x))`. It must work for *any* types, so it is generic:

   ```python
   compose_two(f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]
   ```

   where `A`, `B` and `C` are three different `TypeVar`s. The `B` that `f` returns is the same `B`
   that `g` accepts, and the result takes an `A` and gives a `C`.

The tests read the hints at runtime: they check the aliases, that your `TypeVar`s are used in the
right places (the same `A` in `f` and in the result, the same `B` in `f` and `g`, and so on), and
that the functions work.

**Example**

```python
compose_two(len, lambda n: n * 10)("abc")   # 30   (str -> int -> int)
count_matching([1, 2, 3, 4], lambda n: n % 2 == 0)   # 2
apply_all(3, [lambda n: n + 1, lambda n: n * 2])     # 8
```

**Remember**: `Callable[[int], int]` lists the parameter types in a **list**, then the return type.
Use `Callable[..., int]` only when you really do not care about the parameters.
