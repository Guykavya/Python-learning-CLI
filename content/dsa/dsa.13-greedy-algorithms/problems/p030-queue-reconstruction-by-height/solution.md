## Approach

Process people from the tallest down; equal heights in increasing `k`. Insert each one at index `k` of the queue built so far.

- **Why index `k` is right now:** everyone already in the queue is at least as tall, so exactly the `k` people in front of index `k` count.
- **Why it stays right later:** every later person is shorter (they are invisible to the `k` of anyone already placed), or of equal height with a larger `k`, inserted at an index past this person's position. So no later insertion changes anyone's count.
- **Why equal heights by `k` ascending:** `(5, 0)` must be placed before `(5, 2)`. If `(5, 2)` went in first and `(5, 0)` were later inserted in front of it, `(5, 2)` would count one extra person.

```python
def reconstruct_queue(people):
    order = sorted(((h, k) for h, k in people), key=lambda p: (-p[0], p[1]))
    queue = []
    for h, k in order:
        queue.insert(k, (h, k))
    return queue
```

## Complexity

Sorting is `O(n log n)`; each `list.insert` shifts up to `n` items: `O(n^2)` in total. For `n = 2000` that is a few million element moves, fast in practice. Space `O(n)`.

## Another way

Shortest first, into **empty seats**. Make a list of `n` empty seats and take people from shortest to tallest. When `(h, k)` is placed, every shorter person already sits somewhere, and they do not count for `k`. Every seat that is still empty will later get someone at least as tall. So `(h, k)` must sit in the seat that has exactly `k` **empty** seats in front of it: the `(k + 1)`-th empty seat.

Equal heights go by `k` **descending**: `(5, 2)` is seated before `(5, 0)`. The one with the larger `k` sits further back, so the equal-height person placed after it lands in one of the empty seats in front of it, which `(5, 2)` already counted.

```python
def reconstruct_queue(people):
    seats = [None] * len(people)
    for h, k in sorted(((h, k) for h, k in people), key=lambda p: (p[0], -p[1])):
        empty = -1
        for i in range(len(seats)):
            if seats[i] is None:
                empty += 1
                if empty == k:
                    seats[i] = (h, k)
                    break
    return seats
```
