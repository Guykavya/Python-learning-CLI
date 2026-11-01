## Approach

For each comparison ask two questions: *are the values equal?* (that is `==`) and *how many
objects were created?* (that decides `is`). The small-int cache and interning are the only ways
two separate computations can end up with one object here.

| Line | Reasoning | Output |
|---|---|---|
| `int("100")` twice | 100 is in -5..256, both calls return the cached object | `True True` |
| `int("1000")` twice | outside the cache: two equal but separate objects | `True False` |
| `-5` and `-6` | -5 is the smallest cached int; -6 is not cached | `True False` |
| `200 + int("56")`, `200 + int("57")` | arithmetic results use the cache too: 256 is cached, 257 is a new object | `256 True 257 False` |
| `float("2.5")` twice | floats have no such cache | `True False` |
| two `"".join(...)` | each join builds a new string; equal text, two objects | `True False` |
| `sys.intern` | interning returns one canonical object for the text `python!` | `True True` |
| `[int("5000")] * 3` | one object, three references to it: one id | `True 1` |
| comprehension | each `int(str(n))` makes a value: 7 comes from the cache, 700 does not | `True False` |

## Full output

```
True True
True False
True False
256 True 257 False
True False
True False
True True
True 1
True False
```

## Complexity

Each comparison is O(1): `is` compares two addresses. (`==` on strings is O(length) in the
worst case, which is one reason interning exists: dictionaries of attribute names compare
interned strings by identity first.)

## Another way

Print `id(...)` of both values instead of `is` to see the same thing as numbers (the ids are
machine-specific). The lesson is the same either way: `is` on ints and strings gives answers that
depend on the implementation and on how the value was made. If you write `x is 1000` in a real
program, Python 3.8+ even warns: `SyntaxWarning: "is" with 'int' literal`.
