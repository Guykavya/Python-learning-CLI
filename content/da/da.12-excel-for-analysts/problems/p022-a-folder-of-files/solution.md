## Approach

One loop over the sorted files, with the three real-world guards: empty file, repeated header row, columns that do not match. Reading everything as text keeps the data exactly as in the files; the type decisions come later (and are explicit).

## Code

```python
from pathlib import Path

import pandas as pd


def combine_folder(folder):
    frames, cols = [], None
    for f in sorted(Path(folder).glob("*.csv")):
        if f.stat().st_size == 0:
            continue
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        d = d[~(d == d.columns).all(axis=1)]
        if cols is None:
            cols = list(d.columns)
        elif set(d.columns) != set(cols):
            raise ValueError(f"columns differ in {f.name}")
        d = d[cols].assign(source=f.name)
        frames.append(d)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
```

## Complexity

O(total rows).

## Another way

`pd.concat` of `pd.read_csv(f).assign(source=f.name)` is the minimum; the guards above are what a real month-end folder needs.
