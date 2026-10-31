# re.sub with backreferences: swap Last, First

A class list was exported as `Last, First`, one name per line. You need `First Last`. In the
replacement string of `re.sub`, `\1` and `\2` (or `\g<1>`, `\g<name>`) insert what the groups
matched, so two groups and a swapped replacement do the whole job.

Write `swap_names(text: str) -> str` in `solution.py`.

- `text` has one or more lines. Each line that is exactly `Last, First` becomes `First Last`.
- **Last** is one name: letters (any language), `'` or `-`, no spaces. Examples: `Baghel`,
  `O'Brien`, `Smith-Jones`.
- **First** is one or more such names separated by single spaces: `Kavya`, `Anna Maria`.
- Between them: a comma, then any number of spaces or tabs (also none).
  Spaces or tabs at the end of the line are dropped.
- Lines that do not have exactly this shape are left **unchanged** (no comma, two commas,
  a name split over two lines, ...).
- Keep every newline, including a final one.

**Example**

```python
swap_names("Baghel, Kavya")
# 'Kavya Baghel'
swap_names("Sharma,Ravi\nSmith-Jones, Anna Maria\nTeacher: Mrs Rao\n")
# 'Ravi Sharma\nAnna Maria Smith-Jones\nTeacher: Mrs Rao\n'
```
