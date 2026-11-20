# Trace Mo's order

Mo's algorithm (chapter section 16) on a small array with block size `B = 3` and the plain sort key `(l // B, r)` (no alternating direction). For every question it prints how many single-element steps the window made and the number of distinct values. Ranges are half-open. Predict **exactly** what this program prints. Do not run it.

```python
a = [3, 1, 3, 2, 1, 3, 2, 2]
queries = [(0, 4), (5, 8), (1, 3), (2, 7), (4, 6)]
B = 3
order = sorted(range(len(queries)), key=lambda i: (queries[i][0] // B, queries[i][1]))
print("order:", order)
count = {}
distinct = 0
cur_l = cur_r = 0
total = 0
for qi in order:
    l, r = queries[qi]
    moves = 0
    while cur_l > l:                      # grow to the left
        cur_l -= 1
        count[a[cur_l]] = count.get(a[cur_l], 0) + 1
        distinct += count[a[cur_l]] == 1
        moves += 1
    while cur_r < r:                      # grow to the right
        count[a[cur_r]] = count.get(a[cur_r], 0) + 1
        distinct += count[a[cur_r]] == 1
        cur_r += 1
        moves += 1
    while cur_l < l:                      # shrink from the left
        count[a[cur_l]] -= 1
        distinct -= count[a[cur_l]] == 0
        cur_l += 1
        moves += 1
    while cur_r > r:                      # shrink from the right
        cur_r -= 1
        count[a[cur_r]] -= 1
        distinct -= count[a[cur_r]] == 0
        moves += 1
    total += moves
    print(f"q{qi} [{l},{r}): moves {moves}, distinct {distinct}")
print("total moves:", total)
```

Write your answer in `answer.txt`, one printed line per line: the order, five question lines, and the total.

## How to work

1. For each question compute the key `(l // 3, r)` and sort the indices by it.
2. Start with the empty window `[0, 0)`. For each question in that order, move the edges in the program's order: grow left, grow right, shrink left, shrink right. Count every single step.
3. After the moves, the window is exactly `[l, r)`: count its distinct values.

## After you answer

1. How many steps would the questions need in their **input** order (q0, q1, q2, q3, q4)? Compare with 17.
2. Why does the right edge only move forward between q2, q0 and q3?
3. Which step order would make the counts negative, and on which question?
