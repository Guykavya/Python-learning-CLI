# Lookahead: password rules in one pattern

A sign-up form says: *at least 8 characters, an upper-case letter, a lower-case letter, a digit,
no spaces*. Each rule is easy alone, but they talk about **different** parts of the string in
**any** order. A lookahead `(?=...)` checks a rule from the current position *without moving*,
so several of them can stand side by side at the start, each looking at the whole password.

Write in `solution.py`:

1. `STRONG_RE`, a **compiled** pattern (`re.compile`) that holds all the rules in one pattern.
2. `strong(pw: str) -> bool` that returns `True` when `STRONG_RE` matches the **whole** password.

The rules:

- at least 8 characters,
- at least one upper-case letter `A`–`Z`,
- at least one lower-case letter `a`–`z`,
- at least one digit `0`–`9`,
- no whitespace anywhere (no space, tab or newline, not even at the end).

Other characters (`!`, `@`, `₹`, ...) are allowed and count towards the length.

**Example**

```python
strong("Abcdefg1")    # True   (exactly 8)
strong("Abcdef1")     # False  (7 characters)
strong("abcdefg1")    # False  (no upper-case letter)
strong("Abcd efg1")   # False  (a space)
strong("1aB?????")    # True   (order does not matter)
```
