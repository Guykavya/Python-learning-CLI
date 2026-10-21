## Walkthrough

- `a = show(3)` prints `6` and stores `None` in `a`. `b = give(3)` prints nothing and stores `6`.
- `print(a, b)` prints `None 6`.
- `print(show(1))`: the inner call prints `2` first, then the outer print shows its result, `None`.
- `give(give(2))` is `give(4)`, which is `8`.
- `maybe(5)` returns `5`; `maybe(-5)` reaches the bare `return`, which gives `None`.
- `give(3) + 1` is `7`. Arithmetic with a returned value works; `show(3) + 1` would crash,
  because you cannot add `None` and an int.

## The exact output

```text
6
None 6
2
None
8
5 None
7
```
