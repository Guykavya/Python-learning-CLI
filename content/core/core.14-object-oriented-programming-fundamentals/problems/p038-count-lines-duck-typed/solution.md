## Approach

**Duck typing:** "if it walks like a duck and quacks like a duck, it is a duck" (chapter section 15).
`count_nonblank` needs one ability from its source: you can loop over it and get strings. It does
not ask `isinstance(source, list)`; it just loops. So lists, tuples, files, `io.StringIO`,
generators, and classes written years later all work without any change.

**The one type check.** A `str` *can* be looped over, but it gives characters. `"ab\n"` would look
like three "lines". Since a string quacks almost the right way and silently gives a wrong answer,
it is worth one explicit check and a clear `TypeError`. Things that cannot be looped over at all
fail by themselves: `for x in 42` raises `TypeError: 'int' object is not iterable`.

**Stopping early.** `first_line` returns from inside the loop, so it reads only as many lines as it
needs. That matters for big files and endless streams (iterators chapter).

**Making your own class fit.** `Lines` becomes a valid source by giving it `__iter__`. Written as a
generator method, every loop gets a fresh generator, so the object can be looped over many times.

## Code

```python
def count_nonblank(source, comment=None):
    if isinstance(source, str):
        raise TypeError("pass lines, not one string (try text.splitlines())")
    count = 0
    for line in source:
        text = line.strip()
        if not text:
            continue
        if comment is not None and text.startswith(comment):
            continue
        count += 1
    return count


def first_line(source):
    for line in source:
        text = line.strip()
        if text:
            return text
    return None


class Lines:
    def __init__(self, text):
        self.text = text

    def __iter__(self):
        for line in self.text.splitlines():
            yield line
```

## Complexity

`count_nonblank` is O(total length of the lines). `first_line` reads only up to the first
non-blank line. `Lines.__iter__` splits the text once per loop: O(n).

## Another way

`count_nonblank` can be one expression:
`sum(1 for line in source if line.strip() and not (comment and line.strip().startswith(comment)))`.
`Lines.__iter__` can be `return iter(self.text.splitlines())`. Both forms keep the duck-typing idea.
The LBYL alternative, checking `isinstance(source, (list, tuple, io.IOBase))` first, rejects
perfectly good sources like `OnlyIter`; that is why Python code usually prefers EAFP.
