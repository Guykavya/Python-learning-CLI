# Trace the two heaps

This is the `MedianFinder` of chapter section 8. It keeps the lower half of the numbers in a max-heap `low` (stored as negatives) and the upper half in a min-heap `high`. The `add` method moves a number in three steps, and it now reports whether the third step happened. Predict **exactly** what the program prints. Do not run it.

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.low = []                              # max-heap (stored as negatives)
        self.high = []                             # min-heap

    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))      # the largest of low goes up
        moved = False
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))  # the smallest of high comes back
            moved = True
        return moved

    def median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2

mf = MedianFinder()
for x in (7, 3, 9, 3, 5, 8):
    moved = mf.add(x)
    note = "  (moved one back)" if moved else ""
    print(f"add {x}: lower {sorted(-v for v in mf.low)}  upper {sorted(mf.high)}  median {mf.median()}{note}")
```

Write your answer in `answer.txt`, one printed line per line (six lines). Copy the format of the `print` exactly: two spaces between the three parts, the lists sorted from small to large, the note `  (moved one back)` (two spaces first) only on lines where the third step of `add` ran. Mind the type of the median: an odd count gives a number from the data, an even count gives `(a + b) / 2`, which is a float, so `5.0` and not `5`.

## How to work

Keep two columns on paper, `low` and `high`, as **sets of numbers** (the order inside a heap does not matter, because the program prints them sorted). For every number do the three steps one after the other and write the result of each step:

1. add the number to `low`;
2. take the **largest** number of `low` and move it to `high`;
3. if `high` now has more numbers than `low`, take the **smallest** number of `high` and move it back to `low`. This is the moment for the note.

After step 3, read the median from the tops.

## After you answer

1. On which adds does the third step happen, and is that a coincidence? Work it out from the sizes of `low` and `high` before the add.
2. After every line, is the largest number of `lower` at most the smallest number of `upper`? Why does step 2 guarantee it?
3. The number `3` arrives twice. Does the second `3` end in the same half as the first? Does it matter for the median?
