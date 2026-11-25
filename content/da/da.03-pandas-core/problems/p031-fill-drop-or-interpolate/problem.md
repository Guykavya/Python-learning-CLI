# Fill, interpolate or drop

Chapter section 11.2. A sensor column has gaps. There is no single right way to handle them; the right one depends
on what the numbers mean. Write `fill_gaps(s, how)` that returns a **new** Series for one of five strategies:

| `how` | result |
|---|---|
| `"drop"` | the gaps removed (the other rows keep their labels) |
| `"zero"` | every gap replaced by `0` |
| `"ffill"` | every gap copied from the last known value before it |
| `"interpolate"` | a straight line between the known neighbours (the default `Series.interpolate()`) |
| `"median"` | every gap replaced by the median of the known values |

Two edge rules, stated so there is no surprise: a gap **before the first known value** stays missing with `"ffill"`
and with `"interpolate"` (there is nothing before it to copy or to draw from); a gap after the last known value
is repeated by `"interpolate"` (the default) and by `"ffill"`. Any other value of `how` raises `ValueError` whose
message contains the bad word. The input Series is not changed.

## Example

```python
import pandas as pd

from solution import fill_gaps

s = pd.Series([float("nan"), 1.0, float("nan"), 4.0, float("nan")], index=list("abcde"))
print(fill_gaps(s, "ffill").tolist())
print(fill_gaps(s, "interpolate").tolist())
print(fill_gaps(s, "drop").index.tolist())
```

```text
[nan, 1.0, 1.0, 4.0, 4.0]
[nan, 1.0, 2.5, 4.0, 4.0]
['b', 'd']
```
