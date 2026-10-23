## Walkthrough

- **A** `v` is `str | None` and `append` wants `str`. error.
- **B** `continue` skips the `None` case, so `v` is `str`. ok.
- **C** the comprehension condition narrows `v` to `str`. ok.
- **D** the items stay `str | None`, but a `list[str]` is promised. error.
- **E** `table.get(key)` is typed `str | None`, whatever the `in` check says. error.
- **F** `table[key]` is typed `str`. ok.
- **G** inside `if a is not None`, `a` is `str`. ok.
- **H** mypy does not combine "not both None" and "a is None": at `return b`, `b` is still `str | None`. error.
- **I** assigning `"default"` in the `if` branch makes `text` a `str` on both paths. ok.
- **J** `t += v` with `v: int | None`: `int + None` is not allowed. error.
- **K** after `if isinstance(r, str): return 0`, `r` is an `int`. ok.
- **L** `parse(text)` is `int | str`, and `str + int` is not allowed. error.

mypy 2.4.0 reports the file lines of A, D, E, H, J and L (4, 22, 27, 42, 54, 72).

## The exact output

```text
A: error
B: ok
C: ok
D: error
E: error
F: ok
G: ok
H: error
I: ok
J: error
K: ok
L: error
```
