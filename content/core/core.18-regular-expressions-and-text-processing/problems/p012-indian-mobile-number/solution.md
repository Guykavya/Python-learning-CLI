## Approach

Split the rules into pieces, write one small pattern per piece, then join them.

- **prefix** `(?:\+91[ -]?|0)?`: either `+91` with an optional single space or hyphen, or `0`; the whole group is optional.
- **first five** `[6-9][0-9]{4}`: starts with 6-9, then four more digits.
- **middle** `[ -]?`: an optional single space or hyphen.
- **last five** `[0-9]{5}`: five more digits.

`(?:...)` is a **non-capturing group**: it groups the alternation without saving a group
(a plain `( ... )` also works here). `\+` is a literal plus. `fullmatch` makes sure nothing
extra sits before or after, and `s.strip()` handles the outer whitespace.

Compiling the pattern once at module level (`re.compile`) gives it a name and avoids re-parsing it.

## Code

```python
import re

MOBILE_RE = re.compile(r"(?:\+91[ -]?|0)?[6-9][0-9]{4}[ -]?[0-9]{5}")


def is_mobile(s: str) -> bool:
    return MOBILE_RE.fullmatch(s.strip()) is not None
```

Why `"0123456789"` fails: the pattern may try the `0` as a prefix (then only 9 digits remain,
starting with 1), or no prefix (then the number starts with 0). Both fail.

## Complexity

O(n) for a string of length n. The pattern has no nested quantifiers, so there is no risk of
slow backtracking.

## Another way

A two-step approach is easier to read for some people: remove one allowed prefix with
`str.startswith` checks, then `re.fullmatch(r"[6-9][0-9]{4}[ -]?[0-9]{5}", rest)`.
With `re.VERBOSE` you can also spread the pattern over several lines with comments.
