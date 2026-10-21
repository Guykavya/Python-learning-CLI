# Why is append cheap on average?

Two programs build a list of `n` numbers:

```python
# Program 1
a = []
for i in range(n):
    a.append(i)
```

```python
# Program 2
b = []
for i in range(n):
    b.insert(0, i)
```

Measured on this machine:

| n | Program 1 (append) | Program 2 (insert at front) |
|---|---|---|
| 10,000 | 0.0008 s | 0.015 s |
| 100,000 | 0.008 s | 1.38 s |

Recall from "Simulate a growing list" that a list stores its items in a block with a fixed capacity, and when the
block is full a bigger block is reserved and every item is copied.

In `answer.md`, explain:

1. Why a single `append` is sometimes expensive, and how expensive it can be.
2. Using a cost table for doubling capacity (start at capacity 1), why `n` appends cost O(n) **in total**. Show
   the sum of the copies and give a bound for it. What does "amortised O(1) per append" mean?
3. What would go wrong if the list grew by a fixed **10 extra slots** each time instead of doubling? Give the total
   cost as a formula.
4. Why Program 2 is O(n^2), and how the measured times support that (what happens to each time when `n` grows ten
   times?).
5. Why "amortised O(1)" is not the same as "every append is O(1)", and one situation where that difference could
   matter.
