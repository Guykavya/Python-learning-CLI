# The huge array that will not go away

Chapter sections 6.1 and 6.4. A colleague's script loads a big file and keeps only the first ten readings:

```python
import numpy as np


def first_readings(path):
    data = np.load(path)          # 1 GB of float64 readings
    return data[:10]              # "only ten numbers, 80 bytes"


summary = [first_readings(p) for p in ["jan.npy", "feb.npy", "mar.npy"]]
```

The function returns, `data` goes out of scope, and yet the process still uses **3 GB** of memory. In `answer.md`
(about 150 to 250 words), explain:

1. Why the memory is not freed although only ten numbers per file are kept.
2. How you can **check** this in Python (two attributes or functions from the chapter).
3. The one-word fix, and why it works.
4. When keeping the view is the *right* choice.

## Example

A start: "`data[:10]` is a basic slice, so it is a **view**: it does not own any memory of its own..."
