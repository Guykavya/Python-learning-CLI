## Approach

Count the words with a dictionary in `O(n)`. The result order is "largest count first, then smallest word". A heap hands out the smallest key first, so use the key `(-count, word)`: the negation turns the biggest count into the smallest number, and the word breaks ties alphabetically without any extra work. Keep the `k` smallest keys: `heapq.nsmallest(k, ...)` does it with a bounded heap.

## Code

```python
import heapq
from collections import Counter


def top_k_frequent(words, k):
    if k <= 0:
        return []
    counts = Counter(words)
    best = heapq.nsmallest(k, counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return [word for word, _ in best]
```

## Complexity

`O(n)` to count, `O(m log k)` to select, `O(m)` memory (`m` different words).

## Another way

Sorting all the different words, `sorted(counts, key=lambda w: (-counts[w], w))[:k]`, is `O(m log m)` and shorter. `Counter.most_common(k)` uses the heap too, but it breaks ties by **first appearance**, not alphabetically, so it does not give the required order for equal counts. A heap with `(count, reversed word)` is awkward for strings (you cannot negate a word): that is why the `(-count, word)` key and `nsmallest` are the clean way.
