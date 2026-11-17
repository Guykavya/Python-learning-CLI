# A max-heap with `heapq`

`heapq` gives only a **min**-heap. Chapter section 5 shows the usual trick for a max-heap: store the **negated** numbers. Wrap the trick in a small class so that nobody who uses it has to think about minus signs:

```python
class MaxHeap:
    def __init__(self, items=()): ...   # from any iterable of numbers
    def push(self, x): ...              # add x
    def pop(self): ...                  # remove and return the LARGEST item
    def peek(self): ...                 # the largest item, not removed
    def __len__(self): ...
```

Rules:

- Use `heapq` (`heappush`, `heappop`, `heapify`) on a list that holds the **negated** numbers. The caller must never see a negated number: `push(5)` then `peek()` gives `5`, not `-5`.
- `pop()` and `peek()` on an empty heap raise `IndexError`.
- `MaxHeap(items)` must **not change** the iterable it receives. Use `heapq.heapify` for the build.
- The items are ints or floats (negative numbers, zero and big ints included).
- Do **not** use `heapq.heappush_max`, `heappop_max` or `heapify_max`: they exist only in Python 3.14 and later, and this course supports Python 3.11. The tests reject them.

## Example

```python
>>> h = MaxHeap([5, 1, 8, 3])
>>> h.peek(), len(h)
(8, 4)
>>> h.push(10)
>>> [h.pop() for _ in range(len(h))]
[10, 8, 5, 3, 1]

>>> g = MaxHeap()
>>> g.push(-2.5); g.push(0); g.push(-7)
>>> g.pop(), g.pop(), g.pop()
(0, -2.5, -7)
```

## Constraints

- `push` and `pop` are `O(log n)`, `peek` and `len` are `O(1)`, the build is `O(n)`.
- Numbers only (negation does not work for strings).

## Think about

There are two places where the sign must change: on the way **in** and on the way **out**. Which methods are they? What goes wrong if you forget one of the two, for example in `peek`?
