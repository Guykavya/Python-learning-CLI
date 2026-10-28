# Explain: why `@contextmanager` needs `try`/`finally`

`contextlib.contextmanager` turns a generator function into a context manager: the code before
`yield` is the set-up and the code after `yield` is the clean-up. Two versions follow. They are the
same except for one `try`/`finally`.

```python
from contextlib import contextmanager

log = []


@contextmanager
def opened(name):
    log.append("open " + name)
    yield name
    log.append("close " + name)


@contextmanager
def safe_opened(name):
    log.append("open " + name)
    try:
        yield name
    finally:
        log.append("close " + name)


try:
    with opened("a"):
        log.append("work a")
        raise RuntimeError("boom")
except RuntimeError as err:
    log.append("caught " + str(err))

try:
    with safe_opened("b"):
        log.append("work b")
        raise RuntimeError("boom")
except RuntimeError as err:
    log.append("caught " + str(err))

for line in log:
    print(line)
```

Output:

```text
open a
work a
caught boom
open b
work b
close b
caught boom
```

In `answer.md` (about 150 to 300 words, plus a short code block), explain:

1. **What happens.** Why is there no `close a` in the output, but there is a `close b`? Say
   exactly where the exception goes inside each generator.
2. **Why it works this way.** What does a class-based context manager have (`__exit__`) that a bare
   generator does not? How does `@contextmanager` deliver the exception to the generator?
3. **The fix.** Show the corrected `opened`.
4. **When it matters.** Name two real resources whose clean-up would be skipped, and say what goes
   wrong in the program.
