# describe() with functools.singledispatch

A debug tool must describe any value in plain words. Instead of a long `if isinstance(...) elif ...`
chain, use `functools.singledispatch`: one base function, plus one registered version per type.

Write `describe(x)` in `solution.py` with `@singledispatch`, and register versions so that:

| Type of `x` | Result |
|---|---|
| anything not listed below (base function) | `f"unknown: {x!r}"` |
| `int` | `"int 5 (odd)"` or `"int 4 (even)"` |
| `bool` | `"bool True"` / `"bool False"` |
| `str` | `f"text {x!r} of length {len(x)}"` |
| `list` | `"list of N: [d1, d2, ...]"` where each `d` is `describe` of the item |

Watch out: `bool` is a subclass of `int`, so without its own version `True` would be described as `int 1 (odd)`.

**Examples**

```python
describe(5)           # 'int 5 (odd)'
describe(-4)          # 'int -4 (even)'
describe(True)        # 'bool True'
describe("ab")        # "text 'ab' of length 2"
describe([1, "a"])    # "list of 2: [int 1 (odd), text 'a' of length 1]"
describe([])          # 'list of 0: []'
describe(2.5)         # 'unknown: 2.5'
describe({"k": 1})    # "unknown: {'k': 1}"
```
