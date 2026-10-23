# TDD: parse_ranges

A printer dialog asks "Which pages?" and the user types `1-3,5,7-9`. Write
`parse_ranges(text)` so that the tests in `test_solution.py` pass. The tests are in TDD order:
each one adds a rule. Work red, green, refactor: pick the first failing test, make it pass, run
again.

The rules, as the tests state them:

- `"5"` gives `[5]`; `"1-3"` gives `[1, 2, 3]` (both ends included);
- pieces are separated by commas, and spaces around pieces and numbers are ignored;
- the result is **sorted** and has **no duplicates** (`"3,1-3"` gives `[1, 2, 3]`);
- blank text gives `[]`;
- a piece that is not a whole number or a range of two whole numbers raises `ValueError` with
  a message containing `"invalid"`. That covers `"a"`, `"1-"`, `"-3"`, `"1-2-3"` and an empty
  piece such as `"1,,2"`;
- a **reversed** range like `"5-3"` raises `ValueError` with a message containing `"reversed"`.

**Examples**

```python
parse_ranges("1-3,5,7-9")   # [1, 2, 3, 5, 7, 8, 9]
parse_ranges(" 2 , 4 - 6 ") # [2, 4, 5, 6]
parse_ranges("3,1-3")       # [1, 2, 3]
parse_ranges("")            # []
parse_ranges("5-3")         # raises ValueError (reversed ...)
```
