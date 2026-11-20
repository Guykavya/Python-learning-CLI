# Regular expression matching

Write `is_match(s, p)` that returns `True` when the pattern `p` matches the **whole** string `s`. The pattern is a tiny regular expression:

- a letter matches itself;
- `.` matches any **one** character;
- `*` means **zero or more** copies of the element just before it. `a*` matches `""`, `"a"`, `"aa"`, ...; `.*` matches any string.

Every `*` in `p` comes right after a letter or a `.` (never at the start, never `**`). Write it yourself, without the `re` module.

## Example

```python
>>> is_match("aa", "a")
False
>>> is_match("aa", "a*")
True
>>> is_match("ab", ".*")
True
>>> is_match("aab", "c*a*b")       # c* is empty, a* = "aa", b
True
>>> is_match("mississippi", "mis*is*p*.")
False
>>> is_match("", "a*b*")
True
```

## Constraints

- `0 <= len(s) <= 300`, `0 <= len(p) <= 300`; `s` has lowercase letters, `p` has lowercase letters, `.` and `*`.
- `O(len(s) * len(p))` time. The tests contain `"a" * 300` against `"a*" * 150 + "b"`: a recursion that tries every count for every `x*` without a memo is exponential (and so is Python's own `re` module on that input: it does not finish within the time limit).

## Think about

The difference from wildcards (p065): here `*` is not a pattern character on its own; `x*` is **one unit** of two characters. With `f(i, j)` = does `s[:i]` match `p[:j]`, if `p[j-1]` is `*`, which **two** choices does the unit `p[j-2] p[j-1]` give? Which of them needs `s[i-1]` to match `p[j-2]`?
