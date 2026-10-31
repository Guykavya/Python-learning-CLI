# Trace: capturing vs non-capturing groups

Brackets in a pattern do two jobs at once: they **group** (so `+` or `|` applies to the whole
bracket) and they **capture** (so the matched text is remembered as a group). Several functions
change what they return when a pattern captures. `(?:...)` groups *without* capturing.

Trace this program.

```python
import re

text = "ababab abx ab"
print(re.findall(r"(ab)+", text))
print(re.findall(r"(?:ab)+", text))

m = re.search(r"(ab)+", "xababab")
print(m.group(0), m.group(1), m.span(), m.span(1))

print(re.findall(r"(a)(b)", "ab ab"))
print(re.findall(r"(?:a)(b)", "ab ab"))

fruit = "red apple, green apple, blue apple"
print(re.findall(r"(red|green) apple", fruit))
print(re.findall(r"(?:red|green) apple", fruit))
print(re.findall(r"red|green apple", fruit))

m = re.search(r"(?:ab)+(c)?", "ababd")
print(m.group(0), m.groups(), len(m.groups()))

print(re.split(r"(-)", "a-b-c"))
print(re.split(r"(?:-)", "a-b-c"))
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- `re.findall` returns whole matches when the pattern has **no** capturing group, the group's
  text when it has **one**, and a tuple of all groups when it has **two or more**.
- When a repeated group like `(ab)+` matches several times, the group remembers only the
  **last** repetition.
- A group that did not take part in the match is `None`.
- `re.split` puts the text of capturing groups into the result list between the pieces.

**Example** (a different program)

```python
print(re.findall(r"(x)y", "xy xy"), re.findall(r"(?:x)y", "xy xy"))
# ['x', 'x'] ['xy', 'xy']
```
