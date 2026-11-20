## Approach

There are two bugs. (1) The wrong kind of heap. To keep the `k` **highest** scores, the score that must leave is the **lowest** of the kept ones, so the root must be the lowest: a plain **min**-heap of the scores. The classmate stored negated scores, which puts the **highest** kept score at the root; then the rule "replace the root if the new score is better" throws the best score away, and the function returns the `k` lowest scores. It passed the classmate's tests because with `k` equal to the number of scores nothing is ever replaced. (2) For `k = 0` the heap never gets an item, and `heap[0]` raises `IndexError`: handle `k <= 0` before the loop.

## Code

```python
import heapq


def top_scores(scores, k):
    if k <= 0:
        return []
    heap = []                              # a MIN-heap of the k best scores: the root is the weakest of them
    for s in scores:
        if len(heap) < k:
            heapq.heappush(heap, s)
        elif s > heap[0]:
            heapq.heapreplace(heap, s)
    return sorted(heap, reverse=True)
```

## Complexity

`O(n log k)` time (one comparison per score, plus a `heapreplace` for the few scores that beat the root), `O(k)` memory.

## Another way

`heapq.nlargest(k, scores)` does the same in one line. `sorted(scores, reverse=True)[:k]` is correct and shorter, but `O(n log n)` and `O(n)` memory: the comparison test rejects it. If you wanted to keep the minus signs you would have to switch the problem around: a max-heap of size `k` of negated scores is the right tool for the `k` **smallest** scores.
