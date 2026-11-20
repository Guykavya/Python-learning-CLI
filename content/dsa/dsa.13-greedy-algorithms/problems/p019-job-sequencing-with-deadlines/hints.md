## Hint 1

Which job would you never want to lose? Look at the jobs from the most profitable down. When a job arrives, is it safe to give it **any** free slot before its deadline, or does the choice of slot matter for the jobs that come later? Think of a job with deadline 3 that grabs slot 1, and a later job with deadline 1.

## Hint 2

Put each job into the **latest** free slot at or before its deadline: early slots are scarce, only tight-deadline jobs can use them. With `n` jobs, no job ever needs a slot later than `n`, so cap the deadline: `min(deadline, n)`.

## Hint 3

```
n = len(jobs)
slot_free = [True] * (n + 1)          # slots 1..n
total = 0
for deadline, profit in jobs sorted by profit, highest first:
    for t from min(deadline, n) down to 1:
        if slot_free[t]:
            slot_free[t] = False; total += profit; break
return total
```

Another way (chapter section 10, "a heap, by deadline"): sort by deadline, push each profit into a min-heap, and pop the smallest whenever the heap holds more jobs than the current deadline.
