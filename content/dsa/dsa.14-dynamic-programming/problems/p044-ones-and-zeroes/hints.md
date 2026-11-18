## Hint 1

Each string is an item with two weights: `z` = its number of zeros and `o` = its number of ones. Its value is 1. The knapsack state needs one number per capacity: `f[i][j]` = the most strings you can pick from those processed so far with at most `i` zeros and at most `j` ones. Base: everything 0 (no strings yet).

## Hint 2

Take or leave the next string: `f[i][j] = max(f[i][j], f[i - z][j - o] + 1)` when `i >= z` and `j >= o`. As in chapter section 10 you can keep one 2-D table and update it in place, but then `f[i - z][j - o]` must still be the **old** value. Go downwards in `i` **and** in `j`. What happens with a string `"0"` if the zeros loop goes upwards?

## Hint 3

```
f = (m + 1) x (n + 1) table of 0
for s in strs:
    z = s.count("0"); o = s.count("1")
    for i from m down to z:
        for j from n down to o:
            f[i][j] = max(f[i][j], f[i - z][j - o] + 1)
return f[m][n]
```
