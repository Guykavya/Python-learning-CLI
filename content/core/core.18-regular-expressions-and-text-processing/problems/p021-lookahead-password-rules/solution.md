## Approach

A lookahead tests something about the text ahead **without consuming it**. Stack three of them
at the start, each with a `.*` in front so it can look anywhere in the password:

```
(?=.*[A-Z])     somewhere there is a capital
(?=.*[a-z])     somewhere there is a small letter
(?=.*[0-9])     somewhere there is a digit
\S{8,}          now consume: 8 or more non-whitespace characters
```

All three lookaheads start at position 0, because none of them moved the position. The final
`\S{8,}` does the real matching, and it enforces two rules at once: the length and "no
whitespace". `fullmatch` makes it cover the whole string.

Why not `^...$`? In Python `$` matches at the end **or just before a final `\n`**, so
`"Abcdefg1\n"` would pass `^...\S{8,}$`. `fullmatch` (or `\Z`) has no such exception.

`[0-9]` is used instead of `\d` because `\d` also accepts digits from other scripts (like
`٣`); the rule says the digits 0–9.

## Code

```python
import re

STRONG_RE = re.compile(r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])\S{8,}")


def strong(pw: str) -> bool:
    return STRONG_RE.fullmatch(pw) is not None
```

## Complexity

Each lookahead scans the password once (with some backtracking of `.*`), so O(n) per rule, O(n)
overall for a fixed number of rules.

## Another way

Plain Python is often clearer, and gives better error messages ("needs a digit"):

```python
def strong(pw):
    return (len(pw) >= 8
            and any("A" <= c <= "Z" for c in pw)
            and any("a" <= c <= "z" for c in pw)
            and any("0" <= c <= "9" for c in pw)
            and not any(c.isspace() for c in pw))
```

The regex version shines when the rule must live in one string, for example in a config file
or an HTML `pattern=` attribute.
