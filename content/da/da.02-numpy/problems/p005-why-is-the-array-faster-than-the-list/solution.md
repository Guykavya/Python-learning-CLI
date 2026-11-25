## Approach

The model answer is in `answer.md`. The whole explanation rests on two facts from Ch. 1.1–1.2: the array stores raw numbers of one type in one block, and therefore the loop over them can run in compiled code without asking "what type is this?" a million times.

## Code

No code: a written explanation. To see question 3 yourself, time `np.array([1, 2, 3]).sum()` against `sum([1, 2, 3])` with the `best_time` helper of Ch. 1.3.

## Complexity

Both versions are O(n); NumPy has a much smaller constant per element and a larger fixed cost per call.

## Another way

You could explain it with a measurement instead of a picture: time the same job on arrays of 10, 1,000 and 1,000,000 elements and watch the speed-up grow (Ch. 17.3 does this).
