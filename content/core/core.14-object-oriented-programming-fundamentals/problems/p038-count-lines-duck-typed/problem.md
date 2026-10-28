# Count lines from anything that gives lines

A code-statistics tool counts the real lines in source code. The lines may come from a list, from
an open file, from an `io.StringIO`, from a generator, or from some class written by someone else.
The function should not care **what** the source is, only that looping over it gives lines.
That is duck typing. Write it in `solution.py`.

**`count_nonblank(source, comment=None)`**

- `source` is anything you can loop over that gives strings (lines). Lines may end with `"\n"`.
- Count the lines that are not blank after `strip()`.
- If `comment` is given (like `"#"`), also skip lines whose stripped text starts with it.
- A single string is iterable too, but looping over it gives **characters**, not lines. So if
  `source` is a `str`, raise `TypeError` with a message that contains `lines`. (This is the one type
  check you need; everything else is duck typing.)
- Something you cannot loop over (like `42`) raises `TypeError` as well (the `for` loop already does
  that by itself).

**`first_line(source)`** returns the first non-blank line, stripped, or `None` if there is none.
It must stop reading as soon as it finds it (the source may be huge, or endless).

**`class Lines`**: `Lines(text)` wraps a block of text. Looping over a `Lines` object gives the
lines of the text one by one (use `text.splitlines()`). You can loop over the same `Lines` object
many times, and each loop starts from the first line. Give it an `__iter__` method; that is all
`count_nonblank` needs.

**Example**

```python
import io

code = "import os\n\n# setup\nx = 1\n   \nprint(x)\n"
count_nonblank(code.splitlines())                 # 4
count_nonblank(io.StringIO(code), comment="#")    # 3
count_nonblank(Lines(code))                       # 4
count_nonblank(line for line in ["a", "", "b"])   # 2
first_line(["", "  ", "  hello  ", "world"])      # 'hello'
first_line([])                                    # None
count_nonblank(code)        # TypeError: pass lines, not one string
```
