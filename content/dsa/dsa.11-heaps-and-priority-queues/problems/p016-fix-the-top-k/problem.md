# Fix the top-k

A classmate wrote `top_scores(scores, k)`: it should return the `k` **highest** scores, highest first, while keeping only a small heap in memory. It is in `starter.py`:

```python
import heapq


def top_scores(scores, k):
    heap = []                              # a max-heap by negation, at most k scores
    for s in scores:
        if len(heap) < k:
            heapq.heappush(heap, -s)
        elif -s > heap[0]:                 # better than the worst kept score?
            heapq.heapreplace(heap, -s)
    return sorted((-v for v in heap), reverse=True)
```

It passes the classmate's own two tests:

```text
top_scores([5, 1, 9], 3)    gives [9, 5, 1]   (correct: k is the number of scores)
top_scores([4, 4, 4], 3)    gives [4, 4, 4]   (correct)
```

But on the example below it returns something else, and for some inputs it crashes:

```python
>>> top_scores([3, 1, 5, 12, 2, 11, 7], 3)
[12, 11, 7]                     # expected
>>> top_scores([3, 1, 5, 12, 2, 11, 7], 0)
[]                              # expected
```

1. Run the starter on both calls. What does it return, and which exception does it raise? Do not guess: look at what the heap holds after each score.
2. After the loop, which scores are in the heap, and why? What does `heap[0]` mean for a heap of **negated** scores, and which kept score does the code replace?
3. Fix the function. Keep it a **bounded heap**: the tests count comparisons on 50,000 scores, and a solution that sorts everything fails the count.

## Rules for the fixed function

- Return a list of the `k` highest scores, **highest first**. Equal scores are all kept.
- `k <= 0` gives `[]`; `k` larger than the number of scores gives all scores, highest first.
- `scores` can be any iterable of numbers; it is read once and never changed.
- The numbers in the tests that count comparisons can be compared but **not negated**, so a repair that keeps the minus signs cannot work.

## Constraints

- `O(n log k)` time, `O(k)` extra memory. Up to `10**5` scores.

## Think about

For the `k` **largest** items, the item that must leave when a better one arrives is the **smallest** of the kept ones. Which kind of heap has that item at the root?
