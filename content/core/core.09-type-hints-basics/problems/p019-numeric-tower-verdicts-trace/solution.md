## Walkthrough

- **A** `float = 3`: an `int` is accepted for a `float`. ok.
- **B** `int = 3.0`: a `float` is not an `int`. error.
- **C** `int = True`: `bool` is a kind of `int`. ok.
- **D** `bool = 1`: an `int` is not necessarily a `bool`. error.
- **E** `float = False`: `bool` is an `int`, and an `int` is accepted for `float`. ok.
- **F** `list[float] = [1, 2]`: the literal is read as a `list[float]` in this place. ok.
- **G** `list[float] = nums`: `nums` is a `list[int]`, and a list is invariant. The other name could append `2.5` to your list of ints. error.
- **H** `tuple[float, ...] = (1, 2)`: each item is an `int`, which fits `float`. ok.
- **I** `tuple[int, ...] = (1, 2.5)`: `2.5` is a `float`, not an `int`. error.
- **J** `dict[str, float] = {"a": 1}`: the value `1` fits `float`. ok.
- **K** `dict[str, int] = {"a": 1.5}`: the value `1.5` is not an `int`. error.

mypy 2.4.0 reports the file lines of B, D, G, I and K (4, 6, 9, 11 and 13).

## The exact output

```text
A: ok
B: error
C: ok
D: error
E: ok
F: ok
G: error
H: ok
I: error
J: ok
K: error
```
