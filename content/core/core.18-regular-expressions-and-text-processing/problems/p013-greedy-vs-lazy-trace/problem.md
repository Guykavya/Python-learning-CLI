# Trace: greedy vs lazy quantifiers

A **greedy** quantifier (`*`, `+`, `?`, `{m,n}`) takes as much as it can and gives characters
back only if the rest of the pattern fails. A **lazy** quantifier (`*?`, `+?`, `??`, `{m,n}?`)
takes as little as it can and takes more only if the rest fails. Both still start at the
**leftmost** position where any match is possible. Trace this program.

```python
import re

html = "<b>bold</b> and <i>it</i>"
print(re.findall(r"<.*>", html))
print(re.findall(r"<.*?>", html))
print(re.findall(r"<[^>]*>", html))
print(re.search(r"\d{2,4}", "1234567").group())
print(re.search(r"\d{2,4}?", "1234567").group())
print(re.findall(r"\d{2,4}", "1234567"))
print(re.findall(r"\d{2,4}?", "1234567"))
print(re.search(r"a.*b", "a1b2b3").group(), re.search(r"a.*?b", "a1b2b3").group())
print(re.search(r"x.*?$", "xyz").group())
print(re.findall(r"\w+?", "abc"))
print(re.sub(r"\s+?", "_", "a  b"))
print(re.search(r"<(.+?)>", "<<a>>").group(1))
print(re.search(r"colou??r", "colour color").group())
print(re.search(r"\d+?\d", "12345").group(), re.search(r"\d+?$", "12345").group())
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- The engine tries start positions from left to right and returns the first start that works. Greedy or lazy only changes **how long** the match from that start is.
- `[^>]` means "any character except `>`".
- `re.sub(p, r, s)` replaces every non-overlapping match of `p` with `r`.
- `findall` continues searching right after the end of the previous match.

**Example** (a different program)

```python
print(re.search(r"a+", "aaa").group(), re.search(r"a+?", "aaa").group())   # aaa a
```
