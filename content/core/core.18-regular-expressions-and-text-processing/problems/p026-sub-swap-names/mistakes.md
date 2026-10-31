- Forgetting `re.MULTILINE`. Then `^` and `$` mean the whole string and only a one-line text is
  changed.
- Writing `re.sub(pattern, r"\2 \1", text, re.MULTILINE)`. The fourth positional argument of
  `re.sub` is **count**, not flags! Use `flags=re.MULTILINE` (or compile the pattern).
- Using `\s*` after the comma: it crosses the newline and joins two lines.
- Using a plain string `"\2 \1"` for the replacement: `\2` and `\1` become control characters.
- Using `(.+), (.+)` for the names. `.+` also takes commas, so `a, b, c` would be "swapped".
- Forgetting `^` and `$`. Then part of a line can be swapped and the rest left behind.
