## What a good answer contains

- `d` is the array of differences `add[i] - add[i - 1]` of the amounts added; the running total rebuilds `add` because
  the sum of differences telescopes.
- A worked single update: `d = [0, 5, 0, 0, -5, 0, 0]`, totals `0 5 5 5 0 0`, and the reason the `-v` goes to `r + 1`
  (inclusive range).
- The linearity argument for many updates: one prefix pass handles them all.
- The `n + 1` slot for `r = n - 1`.
- O(q n) against O(n + q), and when the simple loop is fine.
- Prefix sums and differences undo each other.

## Rate yourself

- 3 points: the meaning of `d` and the telescoping sum.
- 2 points: a correct single-update trace and why `r + 1`.
- 2 points: why one prefix pass is enough for all updates.
- 1 point: the extra slot.
- 2 points: the costs and the inverse relation.

8 or more means you can use the trick and also rebuild it in 2D (corners of a rectangle) without memorising it.
