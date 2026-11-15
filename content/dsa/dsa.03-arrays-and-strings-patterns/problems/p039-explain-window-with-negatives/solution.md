## What a good answer contains

- The monotonic property: with positive numbers, growing the window raises the sum and shrinking lowers it. The
  window's "shrink while good, grow while bad" rule is only safe because of that.
- A correct hand run of `5 -10 3 4`, `s = 7`: totals 5, -5, -2, 2; the code prints 0; the answer is 2 (`3 4`).
- The reason: a prefix with a negative sum (`5 -10`) should be dropped to **raise** the total, but the code never
  drops anything while the total is below `s`.
- A failing exact-sum example, such as `1 -1 1` with `k = 1` (window counts 2, the answer is 3).
- Correct replacements: prefix sums + dictionary (count), prefix sums + first index (longest), prefix sums + monotonic
  deque (shortest with sum at least `s`), Kadane (largest sum), each O(n).

## Rate yourself

- 2 points: you stated both halves of the monotonic property.
- 3 points: your hand run of the counterexample is correct and you named the right answer.
- 2 points: you explained which part should have been dropped and why the code never drops it.
- 1 point: you gave a failing exact-sum example.
- 2 points: you named a correct method for at least three of the four tasks.

8 or more means you can tell when a sliding window is safe. Below 6: redo problem p028 and p021, and compare.
