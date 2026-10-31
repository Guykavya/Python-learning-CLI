## Approach

Take the one-line pattern apart, piece by piece, and give each piece its own line and comment.
`re.VERBOSE` ignores the layout whitespace and the comments, so the behaviour is unchanged.

The area code needs care. One idea is two groups with the same name,
`\((?P<area>\d{3})\)|(?P<area>\d{3})`, but Python raises `re.error: redefinition of group name`.
Another idea is `\(?\d{3}\)?`, but that accepts `(555` and `555)`. The clean way is an
alternation **inside** one group: `(?P<area>\([2-9]\d{2}\)|[2-9]\d{2})`. Either both brackets or
none. The brackets end up in the group, so strip them in Python.

Verbose-mode details:

- A space you mean must be in a class `[ ]`, escaped `\ `, or written `\s`. Inside `[-. ]` the
  space is kept.
- Use a **raw** triple-quoted string so `\d` and `\(` reach the regex engine unchanged.

`groupdict()` includes every named group; `ext` is `None` when the extension is missing.

## Code

```python
import re

PHONE_RE = re.compile(r"""
    (?:\+1[ -]?)?                    # optional country code: +1, then a space or hyphen
    (?P<area>                        # area code, first digit 2-9 ...
        \([2-9]\d{2}\)               #   ... in brackets: (555)
      | [2-9]\d{2}                   #   ... or bare: 555
    )
    [-. ]?                           # optional separator (a space inside [] is kept)
    (?P<exchange>\d{3})              # exchange
    [-. ]?                           # optional separator
    (?P<line>\d{4})                  # line number
    (?:                              # optional extension
        \s*(?:ext\.?|x)\s*           #   'ext', 'ext.' or 'x'
        (?P<ext>\d{1,5})             #   1 to 5 digits
    )?
""", re.VERBOSE)


def parse_phone(s: str) -> dict | None:
    m = PHONE_RE.fullmatch(s.strip())
    if m is None:
        return None
    result = m.groupdict()
    result["area"] = result["area"].strip("()")
    return result
```

## Complexity

O(n) for a string of length n; every part has a bounded length.

## Another way

To force the **same** separator in both places (reject `555-123.4567`), capture the first one
and repeat it with a backreference: `(?P<sep>[-. ]?)` ... `(?P=sep)`. Then remove `sep` from the
returned dict. Some teams prefer a two-step approach instead: delete everything that is not a
digit with `re.sub(r"\D", "", s)` and check the length and the leading digits. It is simpler,
but it also accepts nonsense like `5-5-5-1-2-3-4-5-6-7`.
