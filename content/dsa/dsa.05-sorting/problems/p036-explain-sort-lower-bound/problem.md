# Explain: why can't comparison sorts beat n log n?

Merge sort, quick sort (on average) and heap sort all take `O(n log n)`, and no algorithm that sorts **only by comparing elements** can do better in the worst case.
Yet counting sort and radix sort sort in `O(n)`. Answer in `answer.md`, in your own words (200 to 350 words):

1. **Possible answers.** For a list of `n` distinct values, how many different orderings could the input be in? So how many different outputs must the algorithm be able to produce?
2. **One comparison.** How many outcomes does a single comparison have? After `k` comparisons, at most how many different situations can the algorithm tell apart?
3. **The bound.** Combine 1 and 2 to get a lower bound on the number of comparisons. Use `n = 4` with numbers: how many comparisons are needed at least?
4. **The escape.** Why does counting sort not break this bound? What does it assume?
5. **When to use what.** Give one case where counting or radix sort beats merge sort and one where it cannot be used.

Then read `solution.md` and `answer.md`, and rate your answer.
