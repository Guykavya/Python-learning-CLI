## Approach

Convert the money to the smallest unit (paise) once, exactly, and do the rest with integers.
Integer division never has rounding errors.

## Code

```python
from decimal import Decimal

total = Decimal(input())
people = int(input())
paise = int(total * 100)
share, left = divmod(paise, people)
print(f"Each pays: {share // 100}.{share % 100:02d}")
print(f"Left over paise: {left}")
```

## Why not float

`4.35` as a float is `4.3499999999999996447...`. Times 100 that is `434.99999999999994`,
and `int()` truncates it to `434`. One paisa disappears. `Decimal("4.35")` has no such error.

## Another way

Print the share as a Decimal: `(Decimal(share) / 100).quantize(Decimal("0.01"))` gives `33.33`.
