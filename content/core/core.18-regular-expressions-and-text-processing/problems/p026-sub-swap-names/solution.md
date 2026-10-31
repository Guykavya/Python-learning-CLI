## Approach

Describe one whole line and capture the two parts:

```
^ ([\w'-]+) , [ \t]* ([\w'-]+(?: [\w'-]+)*) [ \t]* $
```

(read without the spaces)

- Group 1 is the last name, group 2 the first names (single spaces between them).
- `re.MULTILINE` makes `^`/`$` work at every line, so one `re.sub` call fixes all lines.
- `[ \t]*` instead of `\s*`: `\s` also matches `\n`, and then `"Doe,\nJane"` would be glued
  into one name across two lines.
- `$` in MULTILINE mode matches just **before** a `\n`, so the newline is not part of the match
  and stays in the text.

The replacement `r"\2 \1"` writes group 2, a space, group 1. It must be a raw string, or
`"\2"` becomes the character with code 2.

## Code

```python
import re

NAME_RE = re.compile(r"^([\w'-]+),[ \t]*([\w'-]+(?: [\w'-]+)*)[ \t]*$", re.MULTILINE)


def swap_names(text: str) -> str:
    return NAME_RE.sub(r"\2 \1", text)
```

## Complexity

O(n) over the text; each line is examined once.

## Another way

Named groups make the replacement self-explaining:

```python
re.sub(r"^(?P<last>[\w'-]+),[ \t]*(?P<first>[\w'-]+(?: [\w'-]+)*)[ \t]*$",
       r"\g<first> \g<last>", text, flags=re.M)
```

Or without regex: loop over `text.split("\n")`, use `line.split(",")`, check there are exactly
two parts and that they look like names, and join the lines back with `"\n"`.
