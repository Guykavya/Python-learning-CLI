# Trace: findall with and without groups

`re.findall` changes what it returns depending on how many **capturing groups** (pairs of
round brackets) the pattern has. That surprises almost everyone the first time. Trace this
program.

```python
import re

text = "id=7, x=10, id=42"
print(re.findall(r"id=\d+", text))
print(re.findall(r"id=(\d+)", text))
print(re.findall(r"(\w+)=(\d+)", text))
print(re.findall(r"z=(\d+)", text))
pairs = re.findall(r"(\w+)=(\d+)", text)
print(pairs[1][0], len(pairs))
print(re.findall(r"(a)|(b)", "ab"))
print(re.findall(r"\d*", "a12"))
print(re.findall(r"(\d)+", "123 45"))
print(re.findall(r"((\d)\d)", "12 34"))
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- No groups: `findall` returns a list of the **whole matches** (strings).
- One group: a list of what that **group** captured (strings).
- Two or more groups: a list of **tuples**, one string per group.
- A group that did not take part in a match gives `''`.
- If a group is repeated, like `(\d)+`, it keeps only its **last** repetition.
- `findall` also reports **empty** matches. After an empty match, the search moves on by one character.

**Example** (a different program)

```python
print(re.findall(r"(\w)=", "a=1 b=2"))   # ['a', 'b']
```
