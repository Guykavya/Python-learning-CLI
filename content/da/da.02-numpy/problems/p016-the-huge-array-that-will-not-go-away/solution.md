## Approach

The model answer is in `answer.md`. The chain of reasons is: slice → view → no own memory → reference to the base → base cannot be freed. The fix breaks the chain at the second step by making the small piece own its data.

## Code

To see it yourself on a smaller scale (Ch. 6.4):

```python
import numpy as np

huge = np.arange(1_000_000)
tiny = huge[:3]
print(tiny.nbytes, tiny.base.nbytes)   # 24 8000000
safe = huge[:3].copy()
print(safe.base)                       # None
```

## Complexity

The view costs O(1) time but keeps O(N) memory alive; the copy costs O(k) time and O(k) memory for the k elements kept.

## Another way

Load less in the first place: `np.load(path, mmap_mode="r")` maps the file instead of reading it all, so slicing only touches the pages it needs (then still `.copy()` what you keep, or the file stays mapped).
