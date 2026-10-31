- Writing the rules in sequence, `[A-Z].*[a-z].*[0-9]`. That forces an order. Lookaheads do not.
- Forgetting `.*` inside the lookahead: `(?=[A-Z])` only checks the **first** character.
- Using `.{8,}` to consume. `.` matches a space, so `"Abcd efg1"` passes. Use `\S{8,}` (or add
  `(?!.*\s)`).
- Using `^...$` with `re.match`/`re.search`: `$` matches before a trailing newline, so
  `"Abcdefg1\n"` passes.
- Returning the Match object. The function should return `True`/`False`: `... is not None`.
- Using `\d` for the digit rule: it also accepts digits like `٣` from other scripts.
