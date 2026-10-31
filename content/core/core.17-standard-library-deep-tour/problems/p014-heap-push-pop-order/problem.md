# Trace: what the heap list looks like

A heap is just a list with a rule: for every index `i`, `h[i] <= h[2*i+1]` and
`h[i] <= h[2*i+2]` (when those children exist). The list is **not sorted**; only `h[0]` is
guaranteed to be the smallest. Tracing the list by hand is the best way to understand why
push and pop cost O(log n).

```python
import heapq

h = []
for x in [5, 3, 8, 1, 9, 2]:
    heapq.heappush(h, x)
    print(h)
print(heapq.heappop(h), h)
print(heapq.heappushpop(h, 4), h)
print(heapq.heappushpop(h, 0), h)
print(heapq.heapreplace(h, 0), h)

nums = [7, 6, 5, 4, 3, 2, 1]
heapq.heapify(nums)
print(nums)
print([heapq.heappop(nums) for _ in range(3)], nums)

m = []
for x in [2, 7, 4]:
    heapq.heappush(m, -x)
print(m, -m[0])
```

Write exactly what it prints in `answer.txt`.

**The rules** (the parent of index `i` is `(i - 1) // 2`; the children are `2*i+1` and `2*i+2`)

- `heappush(h, x)`: append `x` at the end, then **bubble up**: while `x` is smaller than its
  parent, swap them.
- `heappop(h)`: the answer is `h[0]`. Remove the **last** item, put it at index 0, then **sift
  down**: while it is bigger than its smaller child, swap it with that smaller child.
- `heappushpop(h, x)`: push then pop, done fast: if `h` is empty or `x <= h[0]`, return `x` and leave `h`
  alone. Otherwise return `h[0]`, put `x` at index 0 and sift down.
- `heapreplace(h, x)`: pop then push: **always** return the old `h[0]`, put `x` at index 0 and sift down.
- `heapify(lst)`: for `i` from `len(lst) // 2 - 1` **down to** 0, sift `lst[i]` down.

**Example** (a different program)

```python
h = [1, 4, 2]
heapq.heappush(h, 0)
print(h)       # [0, 1, 2, 4]   0 swaps with 4, then with 1
```
