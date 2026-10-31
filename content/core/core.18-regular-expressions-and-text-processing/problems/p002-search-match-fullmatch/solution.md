## Walkthrough

1. `"cat"`: `cat` is found at 0, it starts at 0, and it is the whole string. All three succeed: `cat cat cat cat`.
2. `"concat"`: `search` finds `cat` at index 3. `match` fails (the text starts with `con`), so `fullmatch` fails too.
3. `"cats"`: starts with `cat`, so `search` and `match` succeed. `fullmatch` fails because the `s` is left over.
4. `"a cat"`: only `search` finds it (index 2).
5. `\d+` on `"42abc"`: `match` takes `42` from position 0. `fullmatch` needs digits up to the end, but `abc` follows: `None`.
6. `search` on `"ab12cd345"` returns the **first** run of digits, `12`, not the longer `345`.
7. `match` on the same text fails at position 0 (`a` is not a digit): `None`.
8. `ca.`: the dot is one character of any kind. `"cat"` is exactly three characters: `cat`. `"cart"` would need four: `None`.
9. `re.match(r"", "xyz")` succeeds with an **empty** match at 0. A Match object is always truthy, so `bool(...)` is `True`, and its `group()` is `""`, so the comparison is `True`.
10. The first `o` in `"foo boo"` is at index 1. `boo` starts at 4 and ends at 7 (one past the last `o`).

## The exact output

```text
cat cat cat cat
concat cat None None
cats cat cat None
a cat cat None None
42 None
12
None
cat None
True True
1 (4, 7)
```

**Lesson:** `match` is "search, but only at 0", `fullmatch` is "match, and also to the end".
For validation ("is the whole input a ...?") reach for `fullmatch`.
