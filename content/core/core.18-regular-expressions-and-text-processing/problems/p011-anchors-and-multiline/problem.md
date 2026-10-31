# Trace: anchors ^ $ \A \Z and MULTILINE

Anchors match a **position**, not a character. `^` and `$` change meaning with the
`re.MULTILINE` flag (short name `re.M`); `\A` and `\Z` never change. And `$` has one famous
quirk with a trailing newline. Trace this program.

```python
import re

s = "abc\n"
print(bool(re.search(r"abc$", s)), bool(re.search(r"abc\Z", s)))
print(bool(re.fullmatch(r"abc", s)), bool(re.match(r"abc$", s)))
lines = "one\ntwo\nthree"
print(re.findall(r"^\w+", lines))
print(re.findall(r"^\w+", lines, re.MULTILINE))
print(re.findall(r"\w+$", lines))
print(re.findall(r"\w+$", lines, re.M))
print(re.findall(r"\A\w+", lines, re.M))
print(re.findall(r"\w+\Z", lines, re.M))
print(re.findall(r"^t\w*", lines, re.M))
print(len(re.findall(r"$", "a\nb\n")))
print(len(re.findall(r"^", "a\nb\n", re.M)))
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

| Anchor | Without MULTILINE | With MULTILINE |
|---|---|---|
| `^` | start of the string | start of the string and just after every `\n` |
| `$` | end of the string, **or just before a final `\n`** | also just before every `\n` |
| `\A` | start of the string only | same |
| `\Z` | very end of the string only | same |

`findall` with a pattern that is only an anchor returns one empty string per position where it matches.

**Example** (a different program)

```python
print(re.findall(r"^\d", "1\n2", re.M), re.findall(r"^\d", "1\n2"))   # ['1', '2'] ['1']
```
