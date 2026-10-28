## Walkthrough

- **A** `s` is a `str`. It could be any string, not only `"r"` or `"w"`. error `[arg-type]`.
- **B** The literal `"r"` has type `Literal['r']`, which is allowed. ok.
- **C** `"x"` is not one of `"r"`, `"w"`. error.
- **D** `m = "w"` gives `m` the type `str` (mypy infers the general type for an ordinary variable, since it could be reassigned). Passing a `str` is an error, even though the value is really `"w"`.
- **E** `n: Final = "w"` is a constant; mypy keeps its exact type, `Literal['w']`. ok.
- **F** `2` is one of the allowed numbers. ok.
- **G** `4` is not allowed. error `[assignment]`.
- **H** `Literal['a']` is a kind of `str`, so it can go into a `str` variable. ok.
- **I** A `str` into `Literal['a']`: the string might be anything. error.
- **J** `mode: Mode = "r"` declares the type `Mode`, so `mode` is a `Mode`, and passing it is fine. ok.
- **K** `"R"` (capital) is not allowed. error.

mypy 2.4.0 reports errors on lines A, C, D, G, I and K.

## The exact output

```text
A: error
B: ok
C: error
D: error
E: ok
F: ok
G: error
H: ok
I: error
J: ok
K: error
```
