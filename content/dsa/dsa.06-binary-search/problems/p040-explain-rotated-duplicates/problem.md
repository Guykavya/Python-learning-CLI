# Explain: why duplicates break the rotated search

For a rotated sorted array with **distinct** values, comparing `a[mid]` with `a[hi]` always decides the side of the minimum. With **duplicates** that stops being true. Answer in `answer.md`, with the small arrays as examples. Aim for 200 to 350 words.

1. **The ambiguity.** Show two arrays with the same `lo`, `mid`, `hi` and `a[mid] == a[hi]` but with the minimum on different sides of `mid`. (For example `[3, 3, 3, 1, 3]` and `[3, 1, 3, 3, 3]`, or build your own.)
2. **The safe move.** Why can you drop `a[hi]` (`hi -= 1`) when `a[mid] == a[hi]` without losing the minimum? What if `a[hi]` itself *is* the minimum?
3. **Why `hi = mid` is wrong** in the equal case (a counterexample).
4. **Worst case.** Which input forces about `n` steps? So what is the worst-case complexity, and why can no algorithm do better in general?
5. **Typical case.** When is the search still fast?

Read `solution.md` and `answer.md`, and rate your answer.
