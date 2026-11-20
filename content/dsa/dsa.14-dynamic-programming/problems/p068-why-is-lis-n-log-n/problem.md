# Explain: why is LIS O(n log n)?

Chapter section 13 gives two ways to find the length of the longest **strictly** increasing subsequence (LIS). The first is an `O(n^2)` DP: `f(i)` = the LIS that ends at `i`, found by looking at every earlier `j`. The second is this:

```python
from bisect import bisect_left

def lis_fast(nums):
    tails = []
    for x in nums:
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
    return len(tails)
```

It looks like a trick. Your job is to explain **why it is correct** and **why it is fast**. Write 10 to 16 sentences in `answer.md`, answering these questions:

1. What exactly does `tails[k]` mean after some of the numbers have been read? (One precise sentence: "among all ... of length ..., the ...".)
2. Why is `tails` always sorted in **strictly** increasing order? Argue it: what would go wrong if `tails[k] >= tails[k + 1]`?
3. When `x` arrives and `k = bisect_left(tails, x)`, why is it right to **replace** `tails[k]` with `x`? Which subsequence of length `k + 1` ends at `x`? Why does `tails` stay sorted?
4. Why is `len(tails)` at the end the LIS length?
5. On `[3, 4, 1]` the final `tails` is `[1, 4]`. Is that an increasing subsequence of the input? What does this tell you about what `tails` stores?
6. Count the work: how many numbers, and how much work per number? Where does the `O(n^2)` DP spend its extra time?
7. For the longest **non-decreasing** subsequence, which one change is needed, and why?

## Example of the level of detail wanted

For question 6, a good answer names the operation: "each of the `n` numbers does one binary search on a sorted list of at most `n` items, `O(log n)`, plus one append or one assignment, `O(1)`". Not only "binary search is fast".

Then compare with the model answer and rate yourself with its checklist.
