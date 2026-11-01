## Approach

For each pair find the **state that survives**: a variable captured by a closure, a default
list, a half-consumed generator, a name rebound by a loop. Then decide whether "before" and "after" differ.

## Trace

**Pair 1** (`1 ...`). `before_1`: each lambda uses the *variable* `i`. After the loop `i` is
`2`, so the three calls give `2 * 10` each: `[20, 20, 20]`. `after_1`: `i=i` makes each lambda
keep its own value (0, 1, 2): `[0, 10, 20]`. **Different.**

**Pair 2** (two lines). `before_2`'s default `bag=[]` is one list created at `def`. The call
`before_2("a")` appends and returns that list; `before_2("b")` appends to the same list and
returns the same list. `print` evaluates both calls first, so both show `['a', 'b']`.
`after_2` makes a fresh list each call: `['a']` and `['b']`. **Different.**

**Pair 3.** `before_3`: `sum(squares)` consumes the generator (0 + 1 + 4 + 9 = 14). `max` then
sees an empty generator and returns the default `-1`: `(14, -1)`. `after_3` uses a list that can
be read twice: `(14, 9)`. **Different.**

**Pair 4.** `before_4`: the comprehension runs in its own scope, so the outer `i` stays `100`:
`(100, [0, 1, 4])`. `after_4`: the loop assigns the outer `i`, last value `2`: `(2, [0, 1, 4])`. **Different.**

**Pair 5.** `v == None` and `v is None` agree for `None`, `0`, `""` and `[]` (only `None` is
equal to `None` here): both give `[True, False, False, False]`. **Same** (for these inputs; `is None` is still
the right spelling because `==` can be overridden by a class).

**Last two lines.** `before_1() == after_1()` is false, so `different`. Then
`before_2("c")` appends to the shared list that already holds `a` and `b`:
`['a', 'b', 'c']`; `after_2("c")` gives `['c']`.

| Line | Output |
|---|---|
| 1 | `1 [20, 20, 20] [0, 10, 20]` |
| 2 | `2 ['a', 'b'] ['a', 'b']` |
| 3 | `2 ['a'] ['b']` |
| 4 | `3 (14, -1) (14, 9)` |
| 5 | `4 (100, [0, 1, 4]) (2, [0, 1, 4])` |
| 6 | `5 [True, False, False, False] [True, False, False, False]` |
| 7 | `different` |
| 8 | `['a', 'b', 'c'] ['c']` |

## Another way

Run it under `python -i` or add `print(id(...))` inside pair 2 to see that both calls return
the same object. For pair 1, print `[cb.__closure__[0].cell_contents for cb in callbacks]`
to see the shared cell.
