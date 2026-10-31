# Trace: lookbehind must have a fixed width

A lookbehind `(?<=...)` checks the text **just before** the current position, without consuming
it. Python's `re` has a rule: the engine must know how many characters to step back, so
everything inside a lookbehind must have **one fixed width**. Patterns that break the rule are
rejected when they are compiled, with a `re.error`.

Trace this program. For every pattern, decide first whether it compiles at all, then what
`findall` returns.

```python
import re

text = "Rs.250 USD 40 $7 -15 5"

patterns = [
    r"(?<=\$)\d+",
    r"(?<=USD )\d+",
    r"(?<=Rs\.)\d+",
    r"(?<=Rs\.|USD )\d+",
    r"(?<=Rs\.|USD)\d+",
    r"(?:(?<=Rs\.)|(?<=USD ))\d+",
    r"(?<=\w{3} )\d+",
    r"(?<=\s+)\d+",
    r"(?<!-)\b\d+",
    r"(?<=[-$])\d+",
]

for p in patterns:
    try:
        found = re.findall(p, text)
        print(p, "->", found)
    except re.error:
        print(p, "-> re.error")
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- Each line is printed as `pattern -> result`, where the pattern is shown as written (a raw
  string, so `\$` prints as `\$`), and `result` is a list like `['7']` or the text `re.error`.
- `findall` with no groups returns the whole matched texts.
- `\b` is a word boundary; `.` and `$` and `-` are not word characters.
- `{3}` is a fixed width; `+`, `*` and `{1,3}` are not. In an alternation, **every** alternative
  must have the same width.

**Example** (a different program)

```python
print(re.findall(r"(?<=#)\w+", "#py #re x"))    # ['py', 're']
try:
    re.compile(r"(?<=#+)\w+")
except re.error:
    print("re.error")                           # re.error
```
