# Flatten a jagged list

Read `n`, then `n` lines of integers. Lines may have different lengths, and a line may be
empty. Flatten all numbers into one list (row by row, left to right) and print:

```
<all numbers separated by spaces, or (empty)>
Total: <sum>
Longest row: <index of the longest row, counting from 0>
```

If several rows tie for longest, use the **first**. If `n` is 0, print `(empty)`, `Total: 0`
and `Longest row: none`.

**Example**

Input:
```
3
1 2
3 4 5

```
Output:
```
1 2 3 4 5
Total: 15
Longest row: 1
```

(The third row is empty.)
