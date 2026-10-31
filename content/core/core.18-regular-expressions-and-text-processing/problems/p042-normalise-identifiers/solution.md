## Approach

1. Strip the line, then `fullmatch` it against
   `([A-Za-z]{2,4}) *[-_/]? *(\d{1,6})`. Each rule is one piece: the prefix group, optional spaces,
   an optional single separator (`?`, not `*`), optional spaces, the digit group.
2. Build the normal form from the two groups: `prefix.upper()` and `digits.zfill(4)`. Working with
   the digit **string** keeps typed zeros of long numbers (`000042` stays `000042`).
3. Dedupe on the normal form with a `set`, appending to the result list only the first time, so
   order is kept.

`[A-Za-z]` is deliberate: `\w` would also accept digits, `_` and non-English letters.

## Code

```python
import re

ID_RE = re.compile(r"([A-Za-z]{2,4}) *[-_/]? *(\d{1,6})")


def normalise_ids(lines: list[str]) -> list[str]:
    result = []
    seen = set()
    for line in lines:
        m = ID_RE.fullmatch(line.strip())
        if m is None:
            continue
        prefix, number = m.groups()
        normal = f"{prefix.upper()}-{number.zfill(4)}"
        if normal not in seen:
            seen.add(normal)
            result.append(normal)
    return result
```

## Complexity

O(total length of the lines). The `set` makes each duplicate check O(1).

## Another way

Format the number with `f"{int(number):04d}"`. It looks the same for most inputs, but `000042`
becomes `0042`: a different id than the one typed. Decide what the business rule is; here the
digits are kept. A dict also dedupes in order: `list(dict.fromkeys(normals))`.
