## Walkthrough

1. `add_tag("x")` uses the default list, created once when the function was defined. It becomes `['x']`, and `a` is that very list.
2. `add_tag("y")` uses **the same list**, which becomes `['x', 'y']`. `b` is that same object, so `a` also shows `['x', 'y']`.
3. `print(a)` and `print(b)` both show `['x', 'y']`, and `a is b` is `True`.
4. `add_tag_safe` creates a fresh list on each call when none is given, so `c` is `['x']`, `d` is `['y']`, and `c is d` is `False`.
5. `add_tag("z", mine)` appends to `mine`, not to the default. `e` is `mine`, so both print `['m', 'z']`.
6. `add_tag("w")` appends to the default list again: `['x', 'y', 'w']`.
7. `add_tag.__defaults__` is a tuple holding the one default value, which is that same list now holding three items.

mypy accepts the whole file (also in `--strict`): the hint `list[str]` is true for `[]`. The trap is invisible to the checker.

## The exact output

```text
['x', 'y']
['x', 'y']
True
['x']
['y']
False
['m', 'z']
['m', 'z']
['x', 'y', 'w']
(['x', 'y', 'w'],)
```
