# Wildcard matching

Write `wildcard_match(s, p)` that returns `True` when the pattern `p` matches the **whole** string `s`. The pattern has letters and two special characters:

- `?` matches exactly **one** character (any character);
- `*` matches **any sequence** of characters, including the empty one.

This is the matching your shell does for file names (`*.py`), and the `fnmatch` module of the standard library. Write your own, without `fnmatch` or `re`.

## Example

```python
>>> wildcard_match("aa", "a")
False
>>> wildcard_match("aa", "*")
True
>>> wildcard_match("cb", "?a")
False
>>> wildcard_match("adceb", "*a*b")       # * = "", a, * = "dce", b
True
>>> wildcard_match("acdcb", "a*c?b")
False
>>> wildcard_match("", "**")              # stars may match nothing
True
```

## Constraints

- `0 <= len(s), len(p) <= 300`. `s` has lowercase letters; `p` has lowercase letters, `?` and `*`.
- `O(len(s) * len(p))` time. Backtracking that tries every length for every `*` is exponential on patterns like `"*a*a*a...*b"`.

## Think about

Use the state of section 15, "Related problems": `f(i, j)` = does `s[:i]` match `p[:j]`? Look at the **last** character of the pattern. A letter or `?` must eat the last letter of `s`. A `*` has two choices: it is **empty** (drop the `*` from the pattern), or it eats the last letter of `s` **and stays** (it may eat more). Which cells do the two choices read?
