# Explain: loop direction, 0/1 vs unbounded

These two functions differ in **one line**, the direction of the capacity loop (chapter sections 10 and 11):

```python
def knapsack_down(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(W, wt[i] - 1, -1):          # high to low
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]

def knapsack_up(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(wt[i], W + 1):              # low to high
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]

print(knapsack_down([2], [10], 7), knapsack_up([2], [10], 7))
```
```text
10 30
```

Write a short explanation (6 to 10 sentences) in `answer.md` that answers:

1. In the 2-D table `f[i][w]`, which **row** does the "take item `i`" option read from? What does that row mean?
2. In the 1-D array, when the update for `g[w]` runs, has `g[w - wt[i]]` already been updated **for the same item** or not? Answer for both loop directions.
3. Use the output `10 30` to explain what `knapsack_up` really computes. Write down the values of `g[2]`, `g[4]` and `g[6]` while `knapsack_up` runs with the single item (weight 2, value 10).
4. So which direction belongs to the 0/1 knapsack, and which to the unbounded knapsack? Why is the **unbounded** knapsack allowed to read a value that already includes the current item?
5. Subset sum (`f[s] = f[s] or f[s - x]`) and "count subsets" (`f[s] += f[s - x]`) use the same one-array trick. Which direction must they use, and why?

## Example of the level of detail wanted

For question 2 a good sentence is: "Going downwards, `w - wt[i]` is **smaller** than `w`, so it is visited **later** in this pass; when we read it, it still holds the value from before item `i`." Name the cells; do not just say "it goes the other way".

Then compare with the model answer and rate yourself.
