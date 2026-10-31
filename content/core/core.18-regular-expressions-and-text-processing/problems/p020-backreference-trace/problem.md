# Trace: backreferences on quotes, tags and repeats

A backreference does not repeat the *pattern* of a group, it repeats the *text* the group
matched. `(['"]).*?\1` therefore ends with the same kind of quote it started with. Trace this
program carefully: one line is a trap about raw strings.

```python
import re

text = """He said "hi", she said 'yo' and "it's" fine."""
for m in re.finditer(r"(['\"])(.*?)\1", text):
    print(m.group(1), m.group(2))

print(re.findall(r"(\w)\1", "bookkeeper"))
print(re.sub(r"(\w)\1+", r"\1", "aaabccdddd"))

print(bool(re.fullmatch(r"(\d+)-\1", "12-12")), bool(re.fullmatch(r"(\d+)-\1", "12-123")))

q = r"(?P<q>['\"]).*(?P=q)"
print(re.fullmatch(q, "'mixed\""), re.fullmatch(q, "'same'").group("q"))

m = re.search(r"<(\w+)>.*?</\1>", "<b>bold</i> <i>it</i>")
print(m.group(0), m.start())

print(re.search(r"(a)\1", "xaAy", re.IGNORECASE).group(0))

print(re.findall("(a)\1", "aa"), re.findall(r"(a)\1", "aa"))
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- `\1` matches the text group 1 matched. `(?P=q)` does the same for the group named `q`.
- In the replacement string of `re.sub`, `\1` inserts group 1's text.
- `print` of a `None` shows `None`. `bool(None)` is `False`, `bool(match)` is `True`.
- In a **normal** (not raw) string, `"\1"` is a single character with code 1, not a backslash
  and a `1`.
- With `re.IGNORECASE`, a backreference also ignores case.

**Example** (a different program)

```python
print(re.findall(r"(.)\1", "aabbc"))   # ['a', 'b']
```
