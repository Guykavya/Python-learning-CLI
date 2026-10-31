## Walkthrough

1. `"\n"` is one newline character; `r"\n"` keeps both characters: `1 2`.
2. `repr("\t")` shows the tab as `'\t'`. The raw string holds a real backslash, which `repr` doubles: `'\\t'`.
3. `"C:\\new"`: the `\\` is one backslash, so 6 characters. `r"C:\new"` is the same 6 characters (without `r`, `\n` would be a newline!). So the two are equal: `True`.
4. `re.escape("1+1=2")`: `+` is special, `=` is not: `1\+1=2`.
5. `re.escape("a.b*c")`: `a\.b\*c`.
6. `re.escape("hello world_9")`: only the space is escaped: `hello\ world_9`.
7. `"\\d"` is the two characters `\d`, which the engine reads as "digit": `True`. `r"\\d"` is three characters; the engine reads `\\` as one literal backslash followed by `d`. `"x7"` has no backslash: `False`.
8. `r"\."` is a literal dot, found twice in `"a.b.c"`. The plain `"."` matches **any** character, so all three characters of `"a.b"` are found.
9. `r"\bcat"`: word boundary then `cat`: matches `cat`. `"\bcat"` (not raw) starts with a backspace character, which `"cat"` does not contain: `None`.
10. `re.escape("2.5")` is `2\.5`, which matches only the real `2.5`. The unescaped `"2.5"` lets the dot match `0` and `x` too.

## The exact output

```text
1 2
'\t' '\\t'
6 6
True
1\+1=2
a\.b\*c
hello\ world_9
True False
['.', '.'] ['a', '.', 'b']
cat None
['2.5'] ['2.5', '205', '2x5']
```

**Lesson:** always write patterns as raw strings, and pass any text you did not write yourself
(user input, file names, prices) through `re.escape` before putting it into a pattern.
