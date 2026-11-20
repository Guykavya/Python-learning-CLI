# Explain: why 4n nodes?

The recursive segment tree of chapter section 3 stores node `i` at `t[i]`, with the root at 1 and the children of `i` at `2i` and `2i + 1`, and allocates `t = [0] * (4 * n)`. A tree over `n` elements has only `2n - 1` nodes.

```python
def max_index(node, lo, hi):
    if hi - lo == 1:
        return node
    mid = (lo + hi) // 2
    return max(max_index(2 * node, lo, mid), max_index(2 * node + 1, mid, hi))

for n in (4, 5, 8, 9, 1025):
    print(n, 2 * n - 1, max_index(1, 0, n), 4 * n)
```
```text
4 7 7 16
5 9 15 20
8 15 15 32
9 17 31 36
1025 2049 4095 4100
```

Write a short explanation (6 to 10 sentences) in `answer.md` that answers:

1. Why does the tree have exactly `2n - 1` nodes, but the largest **index** can be much bigger?
2. What is the **height** of the tree (number of levels below the root) for `n` elements? Why is it `ceil(log2(n))`?
3. With heap numbering, what is the largest index possible on the bottom level, in terms of the height? Use it to show that the largest index is less than `4n`.
4. Why is `2n` enough when `n` is a **power of two**, and why does `n = 9` need almost `4n`?
5. The iterative tree of chapter section 6 uses exactly `2n`. What does it do differently?

Then compare with the model answer and rate yourself.
