**1. The ambiguity.** Take `[3, 3, 3, 1, 3]` and `[3, 1, 3, 3, 3]`. For both, `lo = 0`, `hi = 4`, `mid = 2` and `a[lo] = a[mid] = a[hi] = 3`. Yet the minimum is on the right of `mid` in the first array and on the left in the second. The three numbers are identical, so no rule that uses only them can tell the sides apart.

**2. The safe move.** If `a[mid] == a[hi]` and `mid < hi`, then dropping `a[hi]` (`hi -= 1`) keeps a copy of that value at `mid`. If `a[hi]` was the minimum, the same value is still in the range, so the minimum **value** is not lost. (The *index* of the minimum may be lost, which is why the problem asks for the value.)

**3. Why `hi = mid` is wrong.** For `[3, 3, 3, 1, 3]` with `mid = 2` and `a[mid] == a[hi]`, `hi = mid` throws away the right side `[1, 3]` and the 1 with it.

**4. Worst case.** In `[1, 1, 1, 1, 0, 1, 1]` almost every step has `a[mid] == a[hi]`, and each such step removes only one element, so about `n` steps are needed: `O(n)`. No algorithm can do better in general: the single 0 can be at any position, and an algorithm that skips a position cannot know whether the 0 is there.

**5. Typical case.** With few repeated values the equal case is rare and the search is still about `log2 n` steps.
