## Walkthrough

After decoration, `add` is `Callable[P, R]` with `P = (a: int, b: int = 0)` and `R = int`. `sub` is
`Callable[..., Any]`.

- **A** `add(1, 2)`: matches `(a: int, b: int = 0)`. ok.
- **B** `add("1", 2)`: a `str` for `a: int`. error `[arg-type]`. The `ParamSpec` kept the real parameters, so the check still works after decoration.
- **C** `add(1, 2, 3)`: three arguments for two parameters. error `[call-arg]` (too many arguments).
- **D** `add(a=1, b=2)`: the parameter **names** also survive a `ParamSpec`, so keywords work. ok.
- **E** `sub("x", "y")`: `Callable[..., Any]` accepts any arguments. ok, although the real function would fail at run time with the wrong types. This is what `...` costs you.
- **F** `reveal_type(add(5))`: `R` is `int`, so `int`.
- **G** `reveal_type(sub(5))`: the result of `Callable[..., Any]` is `Any`.
- **H** `reveal_type(parse("5"))`: the first overload takes `str` and returns `int`.
- **I** `reveal_type(parse(b"5"))`: the first overload does not fit `bytes`, the second does, so `float`.
- **J** `parse(5)`: neither `str` nor `bytes`. error `[call-overload]` (no overload variant matches). The implementation's `str | bytes` is not part of the public signature.

mypy 2.4.0 reports lines 40, 41 and 48 (B, C, J) and prints the four revealed types `int`, `Any`,
`int`, `float` (its own notes write `builtins.int`; the answer uses the plain hint spelling).

## The exact output

```text
A: ok
B: error
C: error
D: ok
E: ok
F: int
G: Any
H: int
I: float
J: error
```
