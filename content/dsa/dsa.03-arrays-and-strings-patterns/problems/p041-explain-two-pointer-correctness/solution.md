## What a good answer contains

- The "too small" argument: `a[j]` is the largest partner still in play, so if `a[i] + a[j]` is too small,
  `a[i]` is useless for every remaining pair.
- The mirror argument for "too big" and `a[j]`.
- An invariant such as "any solution `(p, q)` satisfies `i <= p` and `q <= j`", with the reason each move keeps it
  and the reason the loop ends.
- The trace of the example, ending at `(2, 3)` (values 4 and 6), and one skipped pair with the reason.
- An unsorted counterexample, and the remark that duplicates do not break the proof.
- O(n) passes (at most `n - 1`), plus O(n log n) if you must sort first.

## The picture

Write all pairs `(i, j)` with `i < j` as the upper triangle of an `n x n` table. The search starts in the top-right
corner. "Too small" deletes the current row (every entry in it is at most the current sum); "too big" deletes the
current column (every entry in it is at least the current sum). It is the same staircase walk as searching a
matrix whose rows and columns are sorted: each step removes a whole row or column that cannot contain the target.

## Rate yourself

- 3 points: the "too small" and "too big" arguments, each using the right extreme value (`a[j]` largest, `a[i]` smallest).
- 3 points: a correct invariant and why the moves keep it.
- 2 points: a correct hand trace and a skipped pair explained.
- 2 points: an unsorted counterexample that really fails, and the cost.

8 or more means you can defend the pattern in an interview, not just use it.
