# Trace: re.split keeps the groups

`re.split(pattern, text)` cuts the text wherever the pattern matches and throws the separators
away, like `str.split`. With one twist: if the pattern has **capturing groups**, the text of every
group is put into the result too, between the pieces. Sometimes that is exactly what you want
(keep the operators of a formula), sometimes it is a surprise.

Trace this program.

```python
import re

print(re.split(r",\s*", "a, b,c"))
print(re.split(r"(,)\s*", "a, b,c"))
print(re.split(r"(,\s*)", "a, b,c"))
print(re.split(r"\d", "x1y22z"))
print(re.split(r"(\d+)", "x1y22z"))
print(re.split(r"(-)|(\+)", "1-2+3"))
print(re.split(r"\s+", "  lead and trail  "))
print(re.split(r",", "a,b,c,d", maxsplit=2))
print(re.split(r"(=)", "key=val=more", maxsplit=1))
print(re.split(r"[;,]", "a;;b,"))
parts = re.split(r"([+*])", "2+3*4")
print(parts[0::2], parts[1::2])
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- Without groups: `[piece, piece, ...]`. With groups: after each piece (except the last) come the
  values of **all** groups, in order, for that match. A group that did not take part gives `None`.
- If a separator is at the very start or end of the text, the piece before or after it is `""`.
  Two separators in a row give an empty piece between them.
- `maxsplit=n` makes at most `n` cuts; the rest of the text stays in the last piece.
- `lst[0::2]` takes items 0, 2, 4, ...; `lst[1::2]` takes items 1, 3, 5, ...

**Example** (a different program)

```python
print(re.split(r"(/)", "a/b"))     # ['a', '/', 'b']
print(re.split(r"/", "/a/"))       # ['', 'a', '']
```
