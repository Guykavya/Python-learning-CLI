# Queue reconstruction by height

People stood in a queue, and then the queue was shuffled. For each person you know a pair `(h, k)`: `h` is their height, and `k` is the number of people **in front of them** in the original queue whose height is **greater than or equal to** `h`.

Write `reconstruct_queue(people)` that returns the original queue as a list of `(h, k)` tuples, front first. The input always comes from a real queue, so exactly one answer exists.

This problem is **not** worked in the chapter. The hints teach the idea: place the tallest people first.

## Example

```python
>>> reconstruct_queue([(7, 0), (4, 4), (7, 1), (5, 0), (6, 1), (5, 2)])
[(5, 0), (7, 0), (5, 2), (6, 1), (4, 4), (7, 1)]
```

Check the answer: `(5, 2)` is third, and in front of it are `5` and `7`, both `>= 5`: two people, so `k = 2`. `(4, 4)` is fifth, and all four people in front of it are taller: `k = 4`.

## Constraints

- `0 <= len(people) <= 2000`, `0 <= h <= 10**6`, `0 <= k < len(people)`.
- The input may be a list of tuples or of two-element lists; return tuples. Do not change the caller's list.

## Think about

A short person is invisible to the `k` of every taller person: they do not count. So if you place the tall people first, can putting a short person somewhere later ever spoil a tall person's `k`?
