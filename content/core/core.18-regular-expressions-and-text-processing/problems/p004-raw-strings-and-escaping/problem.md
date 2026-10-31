# Trace: raw strings and escaping

A backslash is read **twice** before a regex runs: first by Python, when it builds the string,
then by the regex engine. A raw string (`r"..."`) switches the first reading off, so the engine
sees exactly what you typed. `re.escape(s)` goes the other way: it adds backslashes so that
every special character in `s` is matched literally. Trace this program.

```python
import re

print(len("\n"), len(r"\n"))
print(repr("\t"), repr(r"\t"))
print(len("C:\\new"), len(r"C:\new"))
print(r"C:\new" == "C:\\new")
print(re.escape("1+1=2"))
print(re.escape("a.b*c"))
print(re.escape("hello world_9"))
print(bool(re.search("\\d", "x7")), bool(re.search(r"\\d", "x7")))
print(re.findall(r"\.", "a.b.c"), re.findall(".", "a.b"))
print(re.search(r"\bcat", "cat").group(), re.search("\bcat", "cat"))
print(re.findall(re.escape("2.5"), "2.5 205 2x5"), re.findall("2.5", "2.5 205 2x5"))
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- In a normal string, `\n` is one newline character, `\t` one tab, `\b` one backspace, and `\\` one backslash. In a raw string they stay as two characters.
- `repr()` of a string shows a single backslash as `\\`.
- `re.escape` puts a backslash before regex special characters such as `. * + ? ( ) [ ] { } | ^ $ \` and also before spaces. Letters, digits, `_` and `=` are left alone.
- To the regex engine, `\d` is a digit, `\\` is one literal backslash, `\.` is a literal dot, and `\b` is a word boundary.

**Example** (a different program)

```python
print(len("a\tb"), len(r"a\tb"))   # 3 4
```
