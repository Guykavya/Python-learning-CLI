# Match object anatomy

A Match object knows **what** matched (`m.group()` or `m.group(0)`) and **where**
(`m.start()`, `m.end()`, `m.span()`). The end is one past the last character, exactly like a
slice: `text[m.start():m.end()] == m.group()`.

Write `span_info(pattern: str, text: str) -> tuple[str, int, int] | None` in `solution.py`.

- Use `re.search` to find the **first** match of `pattern` in `text`.
- Return `(matched_text, start, end)`.
- Return `None` if there is no match.
- Careful: some patterns match the **empty string**. An empty match is still a match:
  `span_info(r"x*", "abc")` is `("", 0, 0)`, not `None`.

**Example**

```python
span_info(r"\d+", "order 66 shipped")   # ('66', 6, 8)
span_info(r"cat", "dog")                # None
span_info(r"x*", "abc")                 # ('', 0, 0)
```
