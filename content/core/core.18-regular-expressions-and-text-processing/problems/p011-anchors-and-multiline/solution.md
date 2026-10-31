## Walkthrough

1. `abc$` succeeds on `"abc\n"`: without MULTILINE, `$` matches at the end **or just before a final newline**. `abc\Z` fails: `\Z` is only the very end, and the `\n` is in the way. `True False`.
2. `fullmatch(r"abc", "abc\n")` must cover all four characters: `False`. `match(r"abc$", ...)` succeeds for the same reason as line 1: `True`. (This is why `fullmatch` is the safe choice for validation.)
3. `^\w+` without flags: `^` is only the start of the string: `['one']`.
4. With `re.MULTILINE`, `^` also matches after each `\n`: `['one', 'two', 'three']`.
5. `\w+$` without flags: only before the end of the string: `['three']`.
6. With `re.M`, `$` also matches before each `\n`: `['one', 'two', 'three']`.
7. `\A` ignores MULTILINE: `['one']`.
8. `\Z` ignores MULTILINE: `['three']`.
9. `^t\w*` with `re.M`: lines that start with `t`: `['two', 'three']`.
10. `$` on `"a\nb\n"` without flags matches at index 3 (before the final newline) and at index 4 (the very end): 2 positions.
11. `^` with `re.M` on `"a\nb\n"` matches at 0, at 2 (after the first `\n`) and at 4 (after the final `\n`, even though no line follows): 3 positions.

## The exact output

```text
True False
False True
['one']
['one', 'two', 'three']
['three']
['one', 'two', 'three']
['one']
['three']
['two', 'three']
2
3
```

**Lesson:** `$` is not "end of string". Use `\Z` or `fullmatch` when a trailing newline must
not sneak through, and use `re.M` when you want `^`/`$` to work per line.
