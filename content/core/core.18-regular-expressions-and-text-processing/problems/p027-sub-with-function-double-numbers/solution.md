## Approach

Two separate jobs:

1. **Find** the integers: a pattern with lookarounds that describes the edges.
2. **Change** them: a function that `re.sub` calls with each Match object.

The pattern:

```
(?<![\w.])   the character before is not a word character or a dot
\d+          the digits
(?!\w|\.\d)  after it: no word character, and not a dot followed by a digit
```

Why the minus sign needs no rule: `-` is not a word character, so in `-4` the `4` is found and
becomes `8`, and the text reads `-8`, which is exactly double of -4. Doubling `-n` and doubling
`n` behind the `-` give the same characters. (For an operation like "add one" that would not be
true: -4 + 1 is -3, not -5, and you would need `-?` with care about `5-3`.)

Why decimals are skipped: in `2.5`, at `2` the lookahead sees `.5` and fails (and `\d+` cannot
shrink to nothing). At `5` the lookbehind sees `.` and fails.

The function: `int(m.group()) * 2` handles leading zeros, and `str(...)` turns it
back into text. `re.sub` must get a **string** back from the function.

## Code

```python
import re

INT_RE = re.compile(r"(?<![\w.])\d+(?!\w|\.\d)")


def _double(m: re.Match) -> str:
    return str(int(m.group()) * 2)


def double_numbers(s: str) -> str:
    return INT_RE.sub(_double, s)
```

## Complexity

O(n) over the string; each lookaround checks one or two characters.

## Another way

A `lambda` keeps it on one line: `INT_RE.sub(lambda m: str(int(m.group()) * 2), s)`.

You could also make the function more general, `scale(s, factor)`, by returning a closure:
`def make(factor): return lambda m: str(int(m.group()) * factor)`. A replacement function can
use anything Python can compute: a dict lookup, a counter, a date conversion.
