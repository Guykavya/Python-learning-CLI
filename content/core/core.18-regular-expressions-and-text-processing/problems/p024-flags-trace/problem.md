# Trace: IGNORECASE, MULTILINE, DOTALL and ASCII

Flags change how parts of a pattern behave without changing the pattern itself:

| Flag | Short | Inline | Effect |
|---|---|---|---|
| `re.IGNORECASE` | `re.I` | `(?i)` | letters match in either case |
| `re.MULTILINE` | `re.M` | `(?m)` | `^` and `$` also match at the start and end of every line |
| `re.DOTALL` | `re.S` | `(?s)` | `.` also matches `\n` |
| `re.ASCII` | `re.A` | `(?a)` | `\w`, `\d`, `\s`, `\b` only know ASCII characters |

Flags are combined with `|`. Trace this program.

```python
import re

text = "Apple pie\nbanana split\nCherry tart"

print(re.findall(r"^\w+", text))
print(re.findall(r"^\w+", text, re.MULTILINE))
print(re.findall(r"\w+$", text))
print(re.findall(r"\w+$", text, re.M))
print(re.findall(r"^[a-z]\w*", text, re.M))
print(re.findall(r"^[a-z]\w*", text, re.M | re.I))

print(re.search(r"pie.banana", text))
print(repr(re.search(r"pie.banana", text, re.DOTALL).group()))
print(len(re.findall(r".", "a\nb")), len(re.findall(r".", "a\nb", re.S)))

print(re.findall(r"(?i)cherry", text))
print(re.findall(r"(?m)t$", text))

print(re.findall(r"\w+", "café naïve"))
print(re.findall(r"\w+", "café naïve", re.ASCII))

p = re.compile(r"x", re.I | re.M)
print(bool(p.flags & re.I), bool(p.flags & re.S))
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- Without MULTILINE, `^` matches only at the start of the string and `$` only at the end (or
  just before a final `\n`).
- `print(None)` shows `None`. `repr` of a string with a newline shows `\n`, inside quotes.
- `p.flags` is a number with one bit per flag; `p.flags & re.I` is non-zero when the flag is on.

**Example** (a different program)

```python
print(re.findall(r"^b", "a\nb"), re.findall(r"^b", "a\nb", re.M))   # [] ['b']
```
