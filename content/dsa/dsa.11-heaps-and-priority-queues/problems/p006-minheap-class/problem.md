# A `MinHeap` class

Build the binary min-heap of chapter sections 3 and 4 as a class, **without `heapq`**.

```python
class MinHeap:
    def __init__(self, items=()): ...   # a heap with these items (any iterable)
    def push(self, x): ...              # add x
    def pop(self): ...                  # remove and return the smallest item
    def peek(self): ...                 # return the smallest item, do not remove it
    def __len__(self): ...              # number of items
```

Rules:

- The items are stored in a plain list in the 0-based array layout (`children of i: 2i + 1, 2i + 2`).
- `pop()` and `peek()` on an empty heap raise `IndexError`.
- `MinHeap(items)` **copies** the items: the list you were given must stay as it was. It turns them into a heap with the **bottom-up** method of section 4 (`sift_down` from the last parent back to the root). Do **not** build it by calling `push` for every item: the tests count comparisons, and for a descending list of 1,000 numbers `n` pushes need about 8,000 comparisons, while the bottom-up build needs fewer than 2,000.
- Items only need to support `<` (numbers, strings, tuples). Equal items are allowed.
- Do not import `heapq` and do not call `sorted` or `.sort`; the tests check your source (they use `heapq` themselves as the judge).

## Example

```python
>>> h = MinHeap()
>>> for x in (4, 1, 7, 3):
...     h.push(x)
>>> h.peek(), len(h)
(1, 4)
>>> [h.pop() for _ in range(len(h))]
[1, 3, 4, 7]

>>> data = [5, 3, 8, 1, 9, 2]
>>> g = MinHeap(data)
>>> g.pop(), g.pop(), data       # data is untouched
(1, 2, [5, 3, 8, 1, 9, 2])
```

## Constraints

- `push` and `pop` are `O(log n)`, `peek` and `len` are `O(1)`, `MinHeap(items)` is `O(n)`.
- Up to `10**5` operations.

## Think about

The chapter has the functions `sift_up` and `sift_down` (and `heapify`). What does each method of the class need? Why can `peek` never be `O(log n)`, while `pop` can never be `O(1)`?
