## Walkthrough

Binary search middles (values `a[mid]`):

| target | middles looked at | binary | linear |
|---|---|---|---|
| 50 | 50 | 1 | 50 |
| 1 | 50, 25, 12, 6, 3, 1 | 6 | 1 |
| 100 | 50, 75, 88, 94, 97, 99, 100 | 7 | 100 |
| 37 | 50, 25, 37 | 3 | 37 |
| 101 | 50, 75, 88, 94, 97, 99, 100, then stop | 7 | 100 |

Output:

```
50 True 50 1
1 True 1 6
100 True 100 7
37 True 37 3
101 False 100 7
```

## Key idea

- Linear search: best case 1 step (the target is first), worst case `n` steps (last or missing). O(n).
- Binary search: each step halves the part still possible, so at most about `log2(n) + 1` steps:
  7 for 100 elements, 20 for a million, 60 for 10^18. O(log n).
- Best and worst cases differ by algorithm and by input: for target 1, linear search wins (1 step against 6).
  Big-O usually describes the worst case, where binary search wins by far.
- The price of binary search is that the list must be sorted, which costs O(n log n) once.
