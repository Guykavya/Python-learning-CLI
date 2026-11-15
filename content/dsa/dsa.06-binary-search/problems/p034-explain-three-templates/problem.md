# Explain: the three binary search templates

The chapter shows three ways to write the loop. Answer in `answer.md` in your own words, with a short code sketch for each. Aim for 250 to 400 words.

1. **Closed** `[lo, hi]` with `while lo <= hi`: what are the initial `lo` and `hi`, what are the two updates, what is the **invariant**, and what are `lo` and `hi` when the loop ends?
2. **Half-open** `[lo, hi)` with `while lo < hi`: same four questions. What does the final `lo` mean when you search for "first index with `a[i] >= x`"?
3. **Shrink** (`lo < hi` with `hi = mid`, closed range `[lo, hi]`): when is it the right choice? What must be true before the loop starts?
4. **Mixing**: Show what goes wrong if you start `hi = n - 1` and use the half-open loop `while lo < hi` with `hi = mid`. Give a tiny input.
5. **The round-up mid**: When you need `lo = mid` (searching the last True), why must `mid = (lo + hi + 1) // 2`? Show the infinite loop with `lo = 3, hi = 4`.
6. **Recommendation**: Which one template would you keep for all problems, and why is "pick one and stick to it" a good rule?

Read `solution.md` and `answer.md`, and rate your answer.
