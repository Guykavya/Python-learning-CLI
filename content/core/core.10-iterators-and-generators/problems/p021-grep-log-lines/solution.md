## Approach

Build a pipeline. `enumerate(lines, start=1)` numbers every line. A generator expression keeps
only the matching ones and strips them. `islice(matches, max_count)` stops after `max_count`
matches. `islice` with `None` as the stop has no limit, so one line covers both cases.

Nothing runs until somebody asks for a value. When `islice` has given its last item, it stops
without asking the expression for another one, so no extra line is read.

## Code

```python
from itertools import islice


def grep(lines, word, max_count=None):
    target = word.lower()
    numbered = enumerate(lines, start=1)
    matches = ((n, line.rstrip()) for n, line in numbered if target in line.lower())
    yield from islice(matches, max_count)
```

## Complexity

O(total length of the lines that are read). O(1) extra memory.

## Another way

A plain loop with a counter. Put the "enough?" check right **after** the `yield`, not at the
top of the loop. At the top, the `for` has already read the next line before you check.

```python
def grep(lines, word, max_count=None):
    if max_count == 0:
        return
    found = 0
    for n, line in enumerate(lines, start=1):
        if word.lower() in line.lower():
            yield n, line.rstrip()
            found += 1
            if found == max_count:
                return
```
