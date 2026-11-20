## Hint 1

Look at the tallest people only (height 7 in the example): `(7, 0)` and `(7, 1)`. Among themselves, their `k` tells you their order directly. Now add the next height, 6. A person `(6, 1)` needs exactly one person `>= 6` in front, and **everyone placed so far is `>= 6`**. Where must they go?

## Hint 2

Sort the people by height **descending**, and for equal heights by `k` **ascending**. Build the queue by inserting each person at **index `k`**. Everyone already in the queue is at least as tall, so index `k` gives exactly `k` such people in front. People inserted later are shorter (or equal with a bigger `k`, so they go behind), and they never change the count of anyone already placed.

## Hint 3

```
order = sorted(people, key=lambda p: (-p[0], p[1]))
queue = []
for h, k in order:
    queue.insert(k, (h, k))
return queue
```

Trace the example: sorted order `(7,0) (7,1) (6,1) (5,0) (5,2) (4,4)`. Queue after each insert: `[70]`, `[70, 71]`, `[70, 61, 71]`, `[50, 70, 61, 71]`, `[50, 70, 52, 61, 71]`, `[50, 70, 52, 61, 44, 71]`.
