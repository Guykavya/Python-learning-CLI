# Explain: why halving is so fast

Binary search finds a number among a million sorted ones in about 20 steps. Answer in `answer.md`, in your own words, with small examples. Aim for 150 to 300 words.

1. **Counting.** How many probes (comparisons with a middle element) does binary search need for 1,000,000 elements in the worst case? For 1,000,000,000? Show the idea with `2^k`.
2. **Doubling.** If the list doubles in size, how many extra probes are needed?
3. **The precondition.** What goes wrong if the list is not sorted? Give a 5-element example where binary search misses a value that is present.
4. **Is it worth it?** If you search a list only once, is "sort and then binary search" faster than a plain linear scan? Give the total costs. When does sorting pay off?
5. **One step.** What single fact does one comparison give that lets you discard half the list?

Then read `solution.md` and `answer.md`, and rate your answer.
