## Approach

Walk the lines with `enumerate(lines, start=1)`, so we always know the line number. Strip
each line. Skip it if it is empty or starts with `#`. If there is no `=`, raise a
`ValueError` with the number. Otherwise split once at the first `=` and yield the cleaned key
and value.

The function never builds a list. It reads one line, yields one pair, and waits. That is why
it can parse a huge file, and why pairs before a bad line reach the caller before the error.

## Code

```python
def parse_settings(lines):
    for number, line in enumerate(lines, start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if "=" not in text:
            raise ValueError(f"line {number}: missing '='")
        key, value = text.split("=", 1)
        yield key.strip(), value.strip()
```

## Complexity

O(total length of the lines) time, O(1) extra memory.

## Another way

Build the pipeline in stages with generator expressions: one stage strips and numbers the
lines, one drops blanks and comments, and a final loop splits and checks. It reads well,
but the error check still needs a normal loop, because a generator expression cannot `raise`.

`str.partition("=")` is another option: it returns `(key, "=", value)`, and the middle part
is `""` when there is no `=`.
