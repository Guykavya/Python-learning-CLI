## Walkthrough

- **A** `[1, 2, 3]` is `list[int]`, so `Sequence[T]` gives `T = int`. Result: `int`.
- **B** A `str` is a `Sequence[str]`. `T = str`. Result: `str`.
- **C** `2.5` is a `float`, so `T = float`, the return is `list[T]`: `list[float]`.
- **D** Both arguments are `str`: `T = str`, result `list[str]`.
- **E** Inner call `wrap(1)` is `list[int]`. The outer call has `x: list[int]`, so `T = list[int]` and the result is `list[list[int]]`.
- **F** The argument is `list[list[int]]`, a `Sequence[list[int]]`, so `T = list[int]`.
- **G** `first([1, 2])` is an `int`; the variable is `str`. error (`[assignment]`).
- **H** `first([1, 2])` is an `int`, accepted where a `float` is expected. ok.
- **I** `a` is an `int` and `b` is `list[int]`: `T = int`, result `int`. ok.
- **J** `a` forces `T = int` but `["a"]` is `list[str]` forces `T = str`. `list` is invariant, so mypy cannot find one `T`: error (`Cannot infer value of type parameter "T"`).
- **K** A `tuple[int, int, int]` is a `Sequence[int]`: `int`.

mypy 2.4.0 prints these revealed types, and reports errors on lines `G` and `J`.

## The exact output

```text
A: int
B: str
C: list[float]
D: list[str]
E: list[list[int]]
F: list[int]
G: error
H: ok
I: ok
J: error
K: int
```
