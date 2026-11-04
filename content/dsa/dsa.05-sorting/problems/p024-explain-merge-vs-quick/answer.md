**1. Where is the work?** Merge sort does almost nothing when splitting (cut at the middle) and all the work after the recursion: merging two sorted halves in `O(n)`. Quick sort does the work **before** the recursion: partition around a pivot in `O(n)`. Afterwards there is nothing to combine, because the two parts are already in the right places.

**2. Worst case.** Merge sort is `O(n log n)` for every input because the halves are always equal. Quick sort is `O(n^2)` when the pivot is always the smallest or largest value, so one part is empty. With the last element as pivot, an already sorted list does this: the pivot is the maximum every time, giving `n` levels of work `n, n-1, n-2, ...`.

**3. Memory.** Merge sort needs an extra `O(n)` array for merging. Quick sort works *in place*: it rearranges the same array by swaps, needing only `O(log n)` for the recursion stack if you recurse into the smaller part first.

**4. Stability.** Merge sort is stable when ties take the left element first. The usual quick sort is not: a partition swap moves an element far away and can jump over an equal element.

**5. Choosing.** Merge sort when you need stability, a guaranteed bound, or you sort linked lists or data on disk (sequential access). Quick sort (with a random or median-of-three pivot) for plain in-memory arrays where speed and low memory matter.
