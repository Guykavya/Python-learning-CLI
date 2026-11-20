# K-th smallest in a sorted matrix

A matrix of numbers has `n` rows and `m` columns. **Every row** is sorted from left to right and **every column** is sorted from top to bottom (equal numbers are allowed). Write `kth_smallest(matrix, k)` that returns the `k`-th smallest number of the whole matrix, counting from `k = 1` for the smallest, and counting repeated numbers as often as they appear.

## Example

```text
 1   5   9
10  11  13
12  13  15
```

```python
>>> matrix = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
>>> kth_smallest(matrix, 1)
1
>>> kth_smallest(matrix, 8)       # sorted: 1 5 9 10 11 12 13 13 15
13
>>> kth_smallest(matrix, 9)
15
```

The sorted list of all numbers is `1, 5, 9, 10, 11, 12, 13, 13, 15`; its 8th item is `13`. The two `13`s count twice.

## Constraints

- `1 <= k <= n * m`; `n` and `m` up to 1,000.
- The matrix may be rectangular. A row or a column may have a single item.
- Do not flatten the whole matrix: the tests give you a matrix whose cells **count how often you read them**. For `k = 1000` in a matrix of 1,000,000 cells you may read at most 100,000 of them.

## Think about

This is the merge of `n` sorted rows, stopped after `k` steps. Which cells can possibly be the next smallest after you have taken some cells? Why can rows beyond the `k`-th be ignored? There is a second solution that does not use a heap at all: how many numbers of the matrix are `<= x`, and how fast can you count them when rows and columns are sorted?
