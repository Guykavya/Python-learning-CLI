# Histogram counts by hand

Chapter section 4.3. A histogram counts how many values fall into each bin. The bins of `[0, 10, 20, 30, 40]` are `[0, 10)`, `[10, 20)`,
`[20, 30)` and `[30, 40]`: each bin includes its **left** edge and excludes its right edge, except the **last** bin, which includes both.

```python
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

values = [3, 7, 10, 12, 18, 20, 20, 25, 29, 30, 35, 40]
bins = [0, 10, 20, 30, 40]
fig, ax = plt.subplots()
counts, edges, _ = ax.hist(values, bins=bins)
print(counts.astype(int).tolist())
print(int(counts.sum()))
print(np.histogram([20], bins)[0].tolist())
print(np.histogram([40], bins)[0].tolist())
print(np.histogram([10], bins)[0].tolist())
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `values = [5, 15]` and the same bins, `np.histogram(values, bins)[0].tolist()` would print `[1, 1, 0, 0]`.

## After you answer

- Which bin gets a value that sits exactly on an edge such as 20?
- Why is 40 counted although `[30, 40)` would not contain it?
