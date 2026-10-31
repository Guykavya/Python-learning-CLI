## Approach

- `\[` and `\]`, `\(` and `\)` are escaped: they are special characters in a regex.
- `([^\]]+)` captures the link text: one or more characters that are not `]`. A negated class
  stops at the first `]` by itself, so two links on one line stay separate. (`.*?` would also
  work here, `.*` would not.)
- `([^)\s]+)` captures the url: no `)` and no whitespace.
- `(?<!!)` is a negative lookbehind: "the character before `[` is not `!`". It looks without
  consuming, so the text before the link is not swallowed by the match.
- The replacement `r'<a href="\2">\1</a>'` puts group 2 (url) and group 1 (text) in place.
  `sub` replaces every match.

## Code

```python
import re

LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")


def md_links(text: str) -> str:
    return LINK.sub(r'<a href="\2">\1</a>', text)
```

## Complexity

O(n) for text of length n: the negated classes never backtrack into each other.

## Another way

Use named groups and `\g<name>` in the replacement, which reads better:

```python
LINK = re.compile(r"(?<!!)\[(?P<text>[^\]]+)\]\((?P<url>[^)\s]+)\)")
LINK.sub(r'<a href="\g<url>">\g<text></a>', text)
```

Or match images too and decide in a replacement function: `(!?)\[...\]\(...\)` and return
`m.group(0)` unchanged when group 1 is `"!"`.
