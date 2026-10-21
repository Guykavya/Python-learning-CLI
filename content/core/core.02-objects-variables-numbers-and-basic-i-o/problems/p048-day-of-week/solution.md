## Approach

Implement the formula exactly, replacing the two "special case" rules with arithmetic tricks
built from `//` and `%`.

## Code

```python
q = int(input())
m = int(input())
year = int(input())
early = (14 - m) // 12          # 1 for January and February, 0 otherwise
y = year - early
m = m + 12 * early
K = y % 100
J = y // 100
h = (q + (13 * (m + 1)) // 5 + K + K // 4 + J // 4 + 5 * J) % 7
print((h + 5) % 7 + 1)
```

## Why the tricks work

- `(14 - m) // 12`: for m = 1 it is 13 // 12 = 1, for m = 2 it is 12 // 12 = 1, for m = 3 it is
  11 // 12 = 0, and for m = 12 it is 2 // 12 = 0.
- Treating Jan and Feb as the end of the previous year puts the leap day at the very end of the
  "year", so the formula never needs to know about leap years in the middle.
- `(h + 5) % 7 + 1`: h = 2 (Monday) becomes 7 % 7 + 1 = 1; h = 1 (Sunday) becomes 6 + 1 = 7;
  h = 0 (Saturday) becomes 5 + 1 = 6.

## Another way

Once you know `if` (core.04), the adjustment reads `if m < 3: m += 12; year -= 1`. Real programs
use `datetime.date(y, m, d).isoweekday()`.
