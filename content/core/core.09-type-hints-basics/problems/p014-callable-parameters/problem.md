# Functions as parameters: Callable

Write four annotated functions in `solution.py`. Import `Callable` from `collections.abc`.

1. `apply_all(func: Callable[[int], int], numbers: list[int]) -> list[int]`: a new list with
   `func` applied to every number.
2. `keep_if(test: Callable[[int], bool], numbers: list[int]) -> list[int]`: only the numbers for
   which `test` returns `True`, in order.
3. `compose(first: Callable[[int], int], second: Callable[[int], int]) -> Callable[[int], int]`:
   return a **new function** that applies `first`, then `second`.
4. `make_adder(n: int) -> Callable[[int], int]`: return a function that adds `n` to its argument.

**Example**

```python
apply_all(lambda x: x * 2, [1, 2, 3])        # [2, 4, 6]
keep_if(lambda x: x > 1, [1, 2, 3])          # [2, 3]
add_then_double = compose(make_adder(1), lambda x: x * 2)
add_then_double(5)                           # 12
```
