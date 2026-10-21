## Walkthrough

- `show(nums)`: one positional argument, the list itself: `args` is `([1, 2, 3],)`.
- `show(*nums)`: three arguments, `(1, 2, 3)`. Adding `*"ok"` spreads two more: `'o'` and `'k'`.
- `show(nums, opts)`: two positionals, a list and a dict; `kw` is still empty, because the dict
  was passed **without** `**`.
- `show(**opts)`: no positionals; `kw` is `{'sep': '-'}`.
- `show(*nums[1:], x=0, **opts)`: positionals 2 and 3, keywords `x` then `sep`.
- `pair(*"xy")` is `pair("x", "y")`. `pair(**{...})` binds by name. `pair(*[10], b=20)` mixes both.
- The last line is `print(1, 2, 3, sep="-")`.

## The exact output

```text
1 ([1, 2, 3],) {}
3 (1, 2, 3) {}
5 (1, 2, 3, 'o', 'k') {}
2 ([1, 2, 3], {'sep': '-'}) {}
0 () {'sep': '-'}
2 (2, 3) {'x': 0, 'sep': '-'}
a=x b=y
a=2 b=1
a=10 b=20
1-2-3
```
