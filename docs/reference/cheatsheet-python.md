# Python cheat sheet

## Types and conversions
`int float str bool list tuple dict set` · `int("5")` `str(5)` `list("ab")` `set([1,1])` · falsy: `0 "" [] {} set() None`

## Strings
`s.split()` `",".join(xs)` `s.strip()` `s.replace(a,b)` `s.startswith(x)` `s.find(x)` (-1 if missing) `s.casefold()`
f-strings: `f"{x:>8.2f}"` `f"{n:,}"` `f"{x!r}"` `f"{x=}"`

## Collections
| | list | dict | set |
|---|---|---|---|
| add | `a.append(x)` | `d[k]=v` | `s.add(x)` |
| remove | `a.pop()` `a.remove(x)` | `d.pop(k, None)` | `s.discard(x)` |
| look up | `x in a` is O(n) | `k in d` is O(1) | `x in s` is O(1) |
Slicing: `a[1:]` `a[:-1]` `a[::-1]` `a[::2]` · `sorted(a, key=f, reverse=True)` (new list) · `a.sort()` (in place)
Comprehensions: `[f(x) for x in xs if c]` `{k: v for ...}` `{x for ...}` · generator: `(f(x) for x in xs)`

## Loops and helpers
`enumerate(xs, 1)` `zip(a, b)` `range(n)` `reversed(xs)` `any(...)` `all(...)` `sum(...)` `min(xs, key=f)` `max(xs, default=0)`
`d.items()` `d.get(k, default)` `d.setdefault(k, [])` · `collections.Counter, defaultdict, deque` · `itertools.chain, groupby, product`

## Functions
`def f(a, b=1, *args, c, **kw)` · `lambda x: x+1` · never use a mutable default (`def f(x=[])`)
Unpacking: `a, *rest = xs` · `{**d1, **d2}` · `f(*args, **kw)`

## Errors
```python
try: ...
except (ValueError, KeyError) as e: ...
else: ...            # no error happened
finally: ...         # always
raise ValueError("why") from err
```
Catch the narrowest exception; never a bare `except:`.

## Files and paths
```python
from pathlib import Path
p = Path("data") / "a.txt"
text = p.read_text(encoding="utf-8")      # always give the encoding
with open(p, "w", encoding="utf-8") as f: f.write("x")
```

## Classes
```python
from dataclasses import dataclass
@dataclass(frozen=True, order=True)
class P: x: int; y: int = 0
```
`__repr__` for developers, `__str__` for users, `__eq__` + `__hash__` together, `@property`, `@classmethod`, `@staticmethod`

## Typing
`list[int]` `dict[str, int]` `int | None` `Callable[[int], str]` `Protocol` `TypedDict` `Literal["a","b"]`

## Tools
`python -m venv .venv` · `pip install -e .` · `pytest -q -x -k name` · `python -m pdb file.py` · `python -X importtime`
