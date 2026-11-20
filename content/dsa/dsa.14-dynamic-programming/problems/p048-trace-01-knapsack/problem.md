# Trace 0/1 knapsack

The one-array 0/1 knapsack of chapter section 10, with a print after every item. Predict **exactly** what this program prints. Do not run it.

```python
wt = [3, 1, 4, 2]
val = [5, 2, 6, 3]
W = 7
g = [0] * (W + 1)
print("start", g)
for i in range(len(wt)):
    for w in range(W, wt[i] - 1, -1):
        g[w] = max(g[w], g[w - wt[i]] + val[i])
    print(f"item {i} ({wt[i]},{val[i]})", g)
print("best:", g[W])
```

Write your answer in `answer.txt`, one printed line per line: the `start` line, one line per item, then the `best:` line.

## How to work

1. Draw the array `g` as 8 boxes, for capacities 0 to 7. All start at 0.
2. For each item, go through `w` from **7 down to the item's weight**. For every `w`, compare the box `g[w]` with `g[w - weight] + value` and keep the larger one.
3. Because you go downwards, the box `g[w - weight]` you read has **not** been changed yet for this item. Read it from the line you wrote for the previous item, not from the boxes you are changing now.
4. Write the whole array after each item, in Python's list format: `[0, 2, 2, 5, ...]`.

## After you answer

1. Which items make the final `best` value? Is there more than one choice of items with that value?
2. During item 1 (weight 1, value 2), `g[4]` becomes 7. Which cell did it read, and why was that cell still 5 and not already changed?
3. If the inner loop went **upwards** (`range(wt[i], W + 1)`), what would `g` be after item 0? And what would `best` be at the end? (Work it out, then check against the solution.)
