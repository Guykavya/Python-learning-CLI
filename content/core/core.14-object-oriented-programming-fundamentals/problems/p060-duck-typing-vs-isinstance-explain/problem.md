# Explain: duck typing, EAFP, LBYL and `isinstance` with ABCs

Three teammates wrote the same helper. It writes a report to "something you can write to":

```python
import io

# Version A (Asha): check the exact type first
def save_a(lines, target):
    if not isinstance(target, io.TextIOWrapper):      # the type of open(..., "w")
        raise TypeError("target must be a file")
    for line in lines:
        target.write(line + "\n")

# Version B (Ben): look before you leap
def save_b(lines, target):
    if not hasattr(target, "write"):
        raise TypeError("target needs a write() method")
    for line in lines:
        target.write(line + "\n")

# Version C (Cy): easier to ask forgiveness than permission
def save_c(lines, target):
    try:
        for line in lines:
            target.write(line + "\n")
    except AttributeError:
        raise TypeError("target needs a write() method") from None
```

The tests call each version with a real file, with `io.StringIO()`, and with this class:

```python
class Shout:
    def __init__(self):
        self.parts = []

    def write(self, text):
        self.parts.append(text.upper())
```

A fourth function, written by Dev, sums "a list of numbers":

```python
def total(numbers):
    if isinstance(numbers, list):
        return sum(numbers)
    raise TypeError("numbers must be a list")
```

In `answer.md` (about 300 to 450 words), explain:

1. **Who accepts what.** For each of A, B and C: does it work with the real file, `io.StringIO()` and
   `Shout()`? Why does A reject things that would have worked?
2. **Duck typing.** What does "if it walks like a duck and quacks like a duck, it is a duck" mean
   for `target`? Which versions use it?
3. **LBYL vs EAFP.** Explain both terms with B and C. Give one advantage of each. Then explain the
   **hidden bug** in C: what happens if `Shout.write` itself has a typo that raises `AttributeError`
   (for example `self.part.append(...)`)? How do you keep the EAFP style but make the `try` block
   smaller?
4. **Where checks race.** Why is `if path.exists(): path.read_text()` a weaker pattern than
   `try: path.read_text() except FileNotFoundError:`?
5. **When `isinstance` is right.** `total(range(5))` and `total((1, 2))` fail. How would you fix it
   with an **abstract base class** from `collections.abc` (or with no check at all)? Give two
   situations where an `isinstance` check is the right tool, for example a `str` that must not be
   treated as an iterable of characters, or validation at the edge of a library.

## Example of the level of detail

"`io.StringIO` has a `write` method that behaves like a file's, but it is not an
`io.TextIOWrapper`, so Version A raises `TypeError` for an object that would have worked perfectly."
A good answer goes on like this for each point.
