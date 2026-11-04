# Explain why the window breaks with negatives

The shrinking sliding window solved "shortest subarray with sum at least `s`" (problem p028) in O(n), but only
because every number was positive. Answer in `answer.md`, in your own words, with small examples. Aim for 250 to
450 words.

Here is the window code from p028 for reference:

```python
best = n + 1
total = 0
l = 0
for r in range(n):
    total += a[r]
    while total >= s:
        best = min(best, r - l + 1)
        total -= a[l]
        l += 1
print(best if best <= n else 0)
```

1. **The property.** Which property of positive numbers does this code rely on? State it as two short facts: one
   about growing the window and one about shrinking it.
2. **A counterexample.** Run the code by hand on `a = 5 -10 3 4` with `s = 7`. Show the value of `total` after each
   `r`. What does the code print, and what is the right answer?
3. **Why it fails.** Explain in two or three sentences what goes wrong in your example. Which part of the array
   should have been dropped, and why does the code never drop it?
4. **Exact sums too.** A window that shrinks "while the sum is too big" and counts windows with sum exactly `k`
   also breaks with negatives. Give a tiny array and `k` where it counts the wrong number. (Try `1 -1 1` with `k = 1`.)
5. **What to use instead.** For each task, name a correct method that works with negative numbers, and its time:
   (a) count subarrays with sum exactly `k`; (b) longest subarray with sum exactly `k`;
   (c) shortest subarray with sum at least `s`; (d) largest subarray sum.

Then read `solution.md` and `answer.md`, and rate your answer.
