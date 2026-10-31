## Walkthrough

- **A** `x.upper()` on an `Any`: any attribute is allowed. ok.
- **B** `x.upper()` on an `object`: `object` has no `upper`. error `[attr-defined]`.
- **C** Inside `isinstance(x, str)` the `object` is narrowed to `str`, so `len(x)` is fine. ok.
- **D** `take_int(a)`: an `Any` fits an `int` parameter. ok.
- **E** `take_int(o)`: an `object` is not an `int`. error `[arg-type]`.
- **F** `s1: str = a`: `Any` is assignable to `str`. ok.
- **G** `s2: str = o`: `object` is not assignable to `str`. error `[assignment]`.
- **H** `o = 42`: an `int` fits into an `object` (everything does). ok.
- **I** `a = 42`: anything fits into `Any`. ok.
- **J** `a.whatever` on an `Any` is again `Any`: **Any**. Any spreads through every expression it touches.
- **K** `len(a)`: `len` returns `int` whatever you pass in, so `int`.
- **L** `show_any(123)` and `show_obj(123)`: both parameters accept an `int`. mypy sees no problem. (At run time both would crash, because an `int` has no `upper`. `Any` hid the crash in `show_any`; `object` correctly flagged it inside `show_obj`.)

mypy 2.4.0 reports lines 9 (B), 25 (E) and 27 (G), and reveals `Any` and `int`.

## The exact output

```text
A: ok
B: error
C: ok
D: ok
E: error
F: ok
G: error
H: ok
I: ok
J: Any
K: int
L: ok
```
