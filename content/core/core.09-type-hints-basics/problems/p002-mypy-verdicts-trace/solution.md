## Walkthrough

- **A** `double(4)`: an `int` for an `int`. ok.
- **B** `double("4")`: a `str` for an `int` parameter. error `[arg-type]`. (Python would run it and return `"44"`, which is why mypy matters.)
- **C** `c: str = double(4)`: the call returns an `int`, the variable is declared `str`. error `[assignment]`.
- **D** `d: float = double(4)`: an `int` is accepted where a `float` is expected. ok.
- **E** `double(2.5)`: a `float` is not an `int`. error `[arg-type]`.
- **F** `double(True)`: `bool` is a kind of `int`, so mypy accepts it. ok.
- **G** `g: int = "7"`: a `str` in an `int` variable. error `[assignment]`.
- **H** `h: str = str(double(1))`: `str(...)` always gives a `str`. ok.

mypy 2.4.0 reports lines 6, 7, 9 and 11 of the file (B, C, E, G).

## The exact output

```text
A: ok
B: error
C: error
D: ok
E: error
F: ok
G: error
H: ok
```
