# Sum numbers read from stdin

A program can read what is piped into it, for example `cat numbers.txt | python total.py`.
Standard input is `sys.stdin`, a file-like object that you can loop over line by line.

Write `total_from_stdin()` in `solution.py`:

- Read `sys.stdin` **line by line** (do not load it all at once).
- Skip blank lines (also lines with only spaces).
- Each other line holds one whole number (maybe with spaces around it). Add them up.
- Print `total: N` to stdout and return `N`.
- A line that is not a whole number raises `ValueError`. Do not hide it.

**Example**

Input on stdin:

```text
10
 5

-3
```

```python
total_from_stdin()    # prints "total: 12", returns 12
```
