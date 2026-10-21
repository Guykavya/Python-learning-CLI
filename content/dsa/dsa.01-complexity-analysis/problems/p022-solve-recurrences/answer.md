Master theorem (practical form): for `T(n) = a T(n/b) + n^d`, compare `a` with `b^d`.
If `a < b^d`, the top level dominates: O(n^d). If `a = b^d`, every level costs the same: O(n^d log n).
If `a > b^d`, the leaves dominate: O(n^(log_b a)).

1. `a = 2, b = 2, d = 1`: `2 = 2^1`, equal. **O(n log n).** Each of the `log2 n` levels does `n` work in total.
2. `a = 1, b = 2, d = 0`: `1 = 2^0`, equal. **O(log n).** `log2 n` levels with 1 unit each.
3. `a = 2, b = 2, d = 0`: `2 > 1`. **O(n^(log2 2)) = O(n).** The tree has about `2n` boxes, each doing 1 unit; the
   leaves dominate.
4. `a = 4, b = 2, d = 1`: `4 > 2`. **O(n^(log2 4)) = O(n^2).** Each level does twice the work of the one above
   (`n`, `2n`, `4n`, ...), so the bottom level (`n^2` leaves) dominates.
5. `a = 1, b = 2, d = 1`: `1 < 2`. **O(n).** The work is `n + n/2 + n/4 + ... < 2n`; the top level dominates.
6. **O(n).** One call per level, `n` levels, 1 unit each: `T(n) = n`.
7. **O(n^2).** The work is `n + (n - 1) + ... + 1 = n(n + 1)/2`.
8. **O(2^n).** Each call makes two calls on `n - 1`, so level `k` has `2^k` calls and there are `n` levels:
   `1 + 2 + 4 + ... + 2^(n-1) = 2^n - 1`.

Matches:

- **(a) Binary search is 2:** one recursive look at half the list plus O(1) work to compare with the middle.
- **(b) Two calls on `n - 1` is 8:** O(2^n). (Real `fib` with `n - 1` and `n - 2` is a little smaller, about
  O(1.62^n), but still exponential.)
- **(c) Recursive sum with an index is 6:** one call on a problem one smaller, plus one addition. (If it copied the
  rest with slicing, each call would cost O(n) and it would be recurrence 7, O(n^2).)
- **(d) Merge sort is 1:** two halves plus a linear merge: O(n log n).

**Why not 6 to 8.** The master theorem only covers problems that shrink by a constant **factor** (`n/b`). In 6 to 8
the problem shrinks by subtracting 1, so the tree has `n` levels instead of `log n`, and the level sums behave
differently. Use a recursion tree or expand the recurrence directly instead.

Key ideas to check: compare a with b^d; 1 is n log n; 2 is log n; 3 is n; 4 is n^2; 5 is n; 6 is n; 7 is n^2; 8 is 2^n;
binary search = 2, double call on n-1 = 8, indexed recursive sum = 6, merge sort = 1; master theorem needs n/b, not n-1.
