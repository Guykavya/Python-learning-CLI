# Trace a range query

The recursive sum segment tree of chapter section 3, with a print for every node the query visits: its index, its range, and whether it is outside the query, inside it (its sum is taken), or partial (split). Ranges are half-open. Predict **exactly** what this program prints. Do not run it.

```python
a = [4, 1, 7, 3, 9, 2, 6, 5]
n = len(a)
t = [0] * (4 * n)

def build(node, lo, hi):
    if hi - lo == 1:
        t[node] = a[lo]
        return
    mid = (lo + hi) // 2
    build(2 * node, lo, mid)
    build(2 * node + 1, mid, hi)
    t[node] = t[2 * node] + t[2 * node + 1]

def query(node, lo, hi, l, r, depth):
    pad = "  " * depth
    if r <= lo or hi <= l:
        print(f"{pad}{node} [{lo},{hi}) outside")
        return 0
    if l <= lo and hi <= r:
        print(f"{pad}{node} [{lo},{hi}) inside {t[node]}")
        return t[node]
    print(f"{pad}{node} [{lo},{hi}) partial")
    mid = (lo + hi) // 2
    return query(2 * node, lo, mid, l, r, depth + 1) + query(2 * node + 1, mid, hi, l, r, depth + 1)

build(1, 0, n)
print("sum:", query(1, 0, n, 2, 6, 0))
print("sum:", query(1, 0, n, 1, 7, 0))
```

Write your answer in `answer.txt`, one printed line per line, **with the indentation** (two spaces per level of recursion).

## How to work

1. Draw the tree for `a = [4, 1, 7, 3, 9, 2, 6, 5]`: node 1 = `[0,8)`, nodes 2, 3 = `[0,4)`, `[4,8)`, nodes 4 to 7 = blocks of 2, nodes 8 to 15 = the leaves. Write each node's sum.
2. For each query, start at node 1. For a node `[lo, hi)`: **outside** if `r <= lo or hi <= l`; **inside** if `l <= lo and hi <= r`; otherwise **partial**: print it, then visit the left child, then the right child, one level deeper.
3. Add the sums of the inside nodes.

## After you answer

1. Which nodes are **inside** in each query? Check that their ranges tile the query range exactly.
2. Why is `[4,6)` inside for `query(2, 6)` but node 7 `[6,8)` outside, although `6` appears in both `[4,6)` and `[6,8)`?
3. How many nodes does each query visit? Compare with the length of the range.
