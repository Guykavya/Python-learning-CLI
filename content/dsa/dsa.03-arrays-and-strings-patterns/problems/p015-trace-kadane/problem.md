# Trace Kadane's algorithm

Kadane's algorithm keeps `cur`, the best sum of a run that ends at the current element, and `best`, the best sum
seen anywhere. This version prints `x cur best` for every element. Predict **exactly** what it prints. Do not run it.

```python
def kadane(a):
    cur = best = a[0]
    print(a[0], cur, best)
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
        print(x, cur, best)
    return best


for a in [[2, -3, 4, -1, 2, -5, 3], [-4, -2, -7]]:
    print("--", a)
    print("answer", kadane(a))
```

Write your answer in `answer.txt`, one line per printed line. Lines look like `-3 -1 2`.

## How to work

Make a table with the columns `x`, `cur + x`, `cur` (the larger of `x` and `cur + x`) and `best`. One row per
element.

## After you answer

1. At which elements did `cur` "start fresh" (take `x` alone)? What was the old `cur` there?
2. Which subarray gives the answer 5? Find its start and end from your table.
3. In the all-negative list, why is the answer not 0?
