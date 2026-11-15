## Model answer

The code is **correct**: `append` adds at the back and `pop(0)` removes the oldest item, so the order is first in, first out. The problem is speed, not correctness.

A Python list stores its items in one contiguous block of memory, item 0 first. `pop(0)` removes the first item, so every other item must **shift** one place to the left to close the gap. For a list of `n` items that is `n - 1` moves, so one `pop(0)` costs **O(n)**. A program that dequeues all `n` items does `(n-1) + (n-2) + ... + 1`, about `n^2 / 2` moves: **O(n^2)** in total. In an earlier test run, emptying a 300,000-item list with `pop(0)` took about 20 seconds.

`pop()` from the end removes the last item and nothing has to move, so it is **O(1)**. That is why a list is a perfect stack (both operations at the end) and a poor queue (one operation at the front).

Use `collections.deque`: `append(x)` to enqueue and `popleft()` to dequeue, both **O(1)**. A deque is built from linked blocks of items with pointers to both ends, so removing at the front only moves the "first" pointer; no item shifts. (A ring buffer, where a fixed array wraps around and a `head` index moves forward, gives the same O(1) idea.)

`pop(0)` is fine when the list is tiny (a handful of items) or the queue is used a few times only: then `n` is so small that the shift costs nothing you can measure. For BFS, simulations and anything with thousands of items, use the deque.

Checklist: your answer should mention
- [ ] the code is **correct** (FIFO order) but **slow**
- [ ] `pop(0)` must **shift** every other item one place left
- [ ] one `pop(0)` is **O(n)**; `n` dequeues are **O(n^2)**
- [ ] `pop()` at the end is **O(1)** because nothing moves
- [ ] **deque** with `append` and `popleft`, both **O(1)**
- [ ] why a deque can do it: pointers to both ends (linked blocks or a ring buffer)
- [ ] small lists: the difference does not matter
