## Approach

The naive pattern `([A-Z]+)+` asks for "one or more blocks, each made of one or more letters", which describes the same
thing as "one or more letters", just in exponentially many ways. When the rest of the pattern fails (the `!` cannot be
followed by `-`), the engine backtracks through every way of splitting the 40 letters: about 2^39 of them. The fix is to
**say what you mean**: a single block of letters, `[A-Z]+`. Then there is only one way to match, and a failure is found in
one pass over the text. `fullmatch` makes the whole text count.

## Code

```python
import re

REF = re.compile(r"[A-Z]+-[0-9]{2}-[0-9]{2}-[0-9]{2}")


def is_valid_ref(s):
    return REF.fullmatch(s) is not None
```

## Complexity

O(n) in the length of the text: no backtracking over groups, because nothing can be matched in two different ways.

## Another way

Without a regex: `head, *rest = s.split("-")`, check `head.isalpha() and head.isupper() and head.isascii()`, check
`len(rest) == 3` and that each part has two characters, all in `"0123456789"`. It cannot freeze, and it is easy to read,
but longer. The general rule: avoid a quantifier on a group that can itself match the same text in several ways
(`(a+)+`, `(a|aa)+`, `(a*)*`), and test any new pattern on a long near-miss.
