# Why append is fast and insert(0) is slow

Building a list of 100,000 numbers with `append` takes a few milliseconds. Building the same
list with `insert(0, x)` takes seconds, and doubling the size makes it about **four** times
slower.

Explain in your own words, in `answer.md`:

1. How CPython stores a list in memory (what is in the list object, and what is not).
2. Why `a[i]` is O(1).
3. What happens when `append` finds the storage full, and why `append` is still O(1)
   **amortised**. Explain what "amortised" means.
4. Why `insert(0, x)` and `pop(0)` are O(n), and why a loop of n of them is O(n²) (which
   explains the "four times slower").
5. What you could do instead if you need to add at the front many times.
