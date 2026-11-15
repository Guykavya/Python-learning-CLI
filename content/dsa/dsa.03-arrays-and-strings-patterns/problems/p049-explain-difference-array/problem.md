# Explain why the difference array works

To add `v` to every element of `a[l..r]` (0-based, inclusive) for many updates, the difference array does only two
writes per update and one prefix-sum pass at the end:

```python
d = [0] * (n + 1)
for l, r, v in updates:
    d[l] += v
    d[r + 1] -= v
total = 0
for i in range(n):
    total += d[i]
    a[i] += total
```

Answer in `answer.md`, in your own words, with small examples. Aim for 200 to 400 words.

1. **What `d` means.** After the updates, what does `d[i]` say about the final array? (Think of `d[i]` as "how much the
   added amount changes when you step from position `i - 1` to position `i`".)
2. **One update.** Take `n = 6` and one update `l = 1`, `r = 3`, `v = 5`. Write `d`, then write the running total
   at each `i`. Explain in one sentence why the `+5` starts at `l` and why the `-5` is placed at `r + 1`, not at `r`.
3. **Many updates.** Why can you put all updates into the same `d` and do the prefix sum only once? (What does the
   prefix sum of a sum of arrays equal?)
4. **The extra slot.** Why does `d` have `n + 1` slots? What would go wrong with `n` slots?
5. **Cost.** Compare with adding `v` in a loop from `l` to `r` for each of `q` updates. Give both costs. When is
   the plain loop actually fine?
6. **The link to prefix sums.** A prefix-sum array turns "range sum" questions into two lookups. A difference array
   turns "range add" updates into two writes. In what sense are these two the **inverse** of each other?

Then read `solution.md` and `answer.md`, and rate your answer.
