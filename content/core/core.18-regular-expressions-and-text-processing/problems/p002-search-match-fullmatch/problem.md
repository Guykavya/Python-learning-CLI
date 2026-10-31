# Trace: search vs match vs fullmatch

The three "find one match" functions differ only in **where** the match may be:

| Function | The match must ... |
|---|---|
| `re.search(p, s)` | start anywhere (first place it fits) |
| `re.match(p, s)` | start at position 0 |
| `re.fullmatch(p, s)` | start at position 0 **and** end at the end of `s` |

Each returns a Match object or `None`. Trace this program.

```python
import re


def show(m):
    if m is None:
        return None
    return m.group()


for text in ["cat", "concat", "cats", "a cat"]:
    print(text, show(re.search(r"cat", text)), show(re.match(r"cat", text)), show(re.fullmatch(r"cat", text)))

print(show(re.match(r"\d+", "42abc")), show(re.fullmatch(r"\d+", "42abc")))
print(show(re.search(r"\d+", "ab12cd345")))
print(show(re.match(r"\d+", "ab12cd345")))
print(show(re.fullmatch(r"ca.", "cat")), show(re.fullmatch(r"ca.", "cart")))
print(bool(re.match(r"", "xyz")), show(re.match(r"", "xyz")) == "")
print(re.search(r"o", "foo boo").start(), re.search(r"boo", "foo boo").span())
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- `m.group()` is the matched text. `m.start()` is where it begins, `m.span()` is `(start, end)`, and `end` is one past the last character.
- `print` shows `None` as `None`.
- The empty pattern `r""` matches the empty string at any position.

**Example** (a different program)

```python
print(show(re.search(r"og", "dog")), show(re.match(r"og", "dog")))   # og None
```
