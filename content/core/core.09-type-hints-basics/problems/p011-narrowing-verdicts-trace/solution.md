## Walkthrough

- **A** `len(name)` with `name: str | None`: `None` has no length. error (`[arg-type]`).
- **B** `if name is None: return 0` leaves the function when `None`, so `name` is a `str` after it. ok.
- **C** inside `if name:` the value is truthy, so not `None`. ok.
- **D** `name.upper() if name else "?"`: the `.upper()` is only used when `name` is truthy. ok.
- **E** `name or "?"`: if `name` is falsy (`None` or `""`) the result is `"?"`, otherwise the `str`. The type is `str`. ok.
- **F** returns `str | None` where `-> str` was promised. error (`[return-value]`).
- **G** the `if name is not None:` branch only prints and does not leave the function, so after it `name` is still `str | None`. error (`[return-value]`).
- **H** `assert name is not None` narrows for the rest of the function. ok.

mypy 2.4.0 reports the file lines of A, F and G (7, 35 and 42).

## The exact output

```text
A: error
B: ok
C: ok
D: ok
E: ok
F: error
G: error
H: ok
```
