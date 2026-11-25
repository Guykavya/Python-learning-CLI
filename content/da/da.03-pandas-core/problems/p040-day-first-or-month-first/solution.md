## Approach

Start from the fact that the same text means two valid dates. Then give a way to **find** the order (impossible values, the source), a way to **say** it (an explicit format) and a way to **check** it (count the losses, look at the range). Compare with `answer.md`.

## Code

```python
import pandas as pd

raw = pd.Series(["03/04/2024", "13/02/2024", "07/08/2024", "31/02/2024"])
first = raw.str.split("/").str[0].astype(int)
second = raw.str.split("/").str[1].astype(int)
print(first.max(), second.max())        # 31 and 8: the first part reaches 31, so it is the day

dates = pd.to_datetime(raw, format="%d/%m/%Y", errors="coerce")
print(dates.isna().sum(), "could not be parsed")   # 1: 31 February
```

## Complexity

Parsing with an explicit `format` is O(n) and faster than letting pandas guess the format per value.

## Another way

For a file you control, ask the exporter to write ISO dates (`2024-04-03`), which are never ambiguous. For files you do not control, keep the raw text column next to the parsed column until the check is done.
