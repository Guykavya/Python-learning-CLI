## Approach

Split the job: *where* a price may start (after a marker) and *what* a price looks like.

**What:** `\d[\d,]*(?:\.\d+)?` — a digit, then digits or commas, then optionally a dot followed
by at least one digit. Because the decimal part needs a digit after the dot, the full stop in
`Rs.40.` is left alone. A comma can be eaten at the end (`499,`), but removing commas before
`float` makes that harmless.

**Where:** a lookbehind checks the text just before the number. Python requires every
lookbehind to have a fixed width, so `(?<=₹|Rs\.)` (widths 1 and 3) is an error. The fix is to
write one lookbehind per width and put them in an alternation:

```
(?:(?<=₹)|(?<=₹ )|(?<=Rs\.)|(?<=Rs\. ))
```

Each one alone is fixed width, which is allowed. Since lookbehinds consume nothing, `findall`
returns only the number. The pattern has no capturing group, so `findall` returns whole matches.

## Code

```python
import re

PRICE_RE = re.compile(r"(?:(?<=₹)|(?<=₹ )|(?<=Rs\.)|(?<=Rs\. ))\d[\d,]*(?:\.\d+)?")


def prices(text: str) -> list[float]:
    return [float(s.replace(",", "")) for s in PRICE_RE.findall(text)]
```

## Complexity

O(n): at each position the lookbehinds compare at most 4 characters, and the number part
moves forward without nested repetition.

## Another way

Match the marker too, and capture only the number:

```python
re.findall(r"(?:₹|Rs\.) ?(\d[\d,]*(?:\.\d+)?)", text)
```

With exactly one capturing group, `findall` returns just the group, so this needs no
lookbehind at all and allows `\s?` freely. Lookbehind is the tool when you need the **match
itself** to exclude the marker, for example in `re.sub` or when reading `m.span()`.
