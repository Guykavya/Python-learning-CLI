# Explain: merge sort versus quick sort

Both sorts split the work in two. Yet Python's own `sorted` is neither of them (it is Timsort, a merge-based method), while many C libraries use a quick sort variant.
Answer in `answer.md`, in your own words (200 to 350 words):

1. **Where is the work?** In merge sort, where does the real work happen: before the recursion (splitting) or after it (merging)? In quick sort?
2. **Worst case.** Give the worst-case time of each and one concrete input that triggers it for a quick sort with the last element as pivot.
3. **Memory.** How much extra memory does each need in its usual form? What does "in place" mean?
4. **Stability.** Which is stable in its usual form? Why is the usual quick sort not?
5. **Choosing.** Give one situation where you would pick merge sort and one where you would pick quick sort.

Then read `solution.md` and `answer.md`, and rate your answer.
