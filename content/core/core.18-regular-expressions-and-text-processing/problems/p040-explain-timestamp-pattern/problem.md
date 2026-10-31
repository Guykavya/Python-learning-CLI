# Explain a real-world pattern: ISO-8601 timestamps

Being able to **read** a regex someone else wrote matters as much as writing one. Here is a
pattern from a log-processing tool. It recognises timestamps in a simplified ISO-8601 style,
like `2025-03-01T09:15:02.5+05:30`.

```python
import re

TIMESTAMP = re.compile(r"""
    \A
    (?P<year>\d{4}) - (?P<month>0[1-9]|1[0-2]) - (?P<day>0[1-9]|[12]\d|3[01])   # date
    [T\x20]                                   # 'T' or one space between date and time
    (?P<hour>[01]\d|2[0-3]) : (?P<minute>[0-5]\d)
    (?: : (?P<second>[0-5]\d)                 # seconds are optional ...
        (?: \. (?P<fraction>\d{1,6}) )?       # ... and so is a fraction after them
    )?
    (?P<tz> Z | [+-] (?:[01]\d|2[0-3]) :? [0-5]\d )?   # optional time zone
    \Z
""", re.VERBOSE)

for s in ["2025-03-01T09:15", "2025-03-01 09:15:02.5+05:30", "2025-02-31T23:59:59Z",
          "2025-03-01T24:00", "2025-03-01T09:15.5", "2025-3-01T09:15", "2025-03-01T09:15:02Z\n",
          "2025-03-01 09:15:02 +0530"]:
    m = TIMESTAMP.match(s)
    print(repr(s), "->", m.groupdict() if m else None)
```

In `answer.md` (about 350 to 550 words), explain:

1. **Piece by piece.** Go through the pattern from `\A` to `\Z` and say in plain English what each
   part accepts. In particular: why is the month `0[1-9]|1[0-2]` and not `\d\d`? Why is the hour
   `[01]\d|2[0-3]`? What does the `(?: ... )?` around the seconds do, and why is the fraction group
   nested **inside** it?
2. **The verbose details.** Why does the pattern write `[T\x20]` instead of `[T ]`? Why are the
   spaces around `-` and `:` harmless?
3. **Predict the output.** For each of the eight strings, say whether it matches, and if it does,
   which groups are `None`. For each string that does not match, name the exact part that fails.
4. **Limits.** Name one invalid timestamp that this pattern **accepts**, and say how you would
   catch it (hint: not with a bigger regex).
5. **Anchors.** Why `\A ... \Z` instead of `^ ... $`? Which of the eight inputs shows the
   difference?

**Example** of the level of detail expected for one part:

> `(?P<year>\d{4})`: exactly four digits, saved in the group `year`. Any four digits are
> accepted, `0000` too: the pattern checks the shape of a year, not whether it makes sense.
