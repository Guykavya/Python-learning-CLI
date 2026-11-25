# A regex that never finishes

Chapter section 4.5. A pattern can be correct on every input you try and still **freeze your program** on one input.
It happens when a quantifier sits inside another quantifier, so that the engine can split the same letters in
exponentially many ways before it gives up. This is called **catastrophic backtracking**.

A colleague checks reference codes like `AB-12-34-56` with this pattern:

```python
import re

NAIVE = re.compile(r"([A-Z]+)+-[0-9]{2}-[0-9]{2}-[0-9]{2}")

def is_valid_ref(s):
    return NAIVE.fullmatch(s) is not None
```

It works on `AB-12-34-56`. But on a **near miss** such as `"A" * 40 + "!"` (forty capital letters and then a character
that cannot continue the code) it keeps trying all the ways to cut 40 letters into groups, and does not return in any
reasonable time. A file with one such value hangs the whole cleaning run. **Do not run the naive pattern on long
near-misses on your own machine** (or put a timeout around it).

Write `is_valid_ref(s)` so that it gives the **same answers** but answers every input in well under a second.

## The rules

A reference is valid when the **whole** text is:

1. one or more capital letters `A`-`Z` (a single block, no hyphens inside it), then
2. `-`, two digits `0`-`9`, `-`, two digits, `-`, two digits.

Nothing before, nothing after (not even a space or a newline). Return `True` or `False` (a real `bool`); never raise an
error for a string.

| text | valid? |
|---|---|
| `AB-12-34-56` | yes |
| `A-00-00-00` | yes |
| `ABCDEF-99-99-99` | yes |
| `ab-12-34-56` | no (lower case) |
| `AB-1-34-56` | no (one digit) |
| `AB-12-34` | no (too short) |
| `AB-12-34-567` | no (three digits at the end) |
| `AB-12-34-56 ` | no (trailing space) |
| `-12-34-56` | no (no letters) |
| `AB-1a-34-56` | no (a letter among digits) |
| the empty text | no |
| `"A" * 40 + "!"` | no, and it must return quickly |

## Example

```python
print(is_valid_ref("AB-12-34-56"), is_valid_ref("AB-12-34"), is_valid_ref("A" * 40 + "!"))
```

```text
True False False
```

The tests run your function on near-misses in a separate process with a 2-second limit.
