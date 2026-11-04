## Walkthrough

First call, `a = [1, 3, 4, 6, 8, 11]`, `target = 10`:

| i | j | a[i] + a[j] | compared with 10 | move |
|---|---|---|---|---|
| 0 | 5 | 1 + 11 = 12 | too big | j-1 |
| 0 | 4 | 1 + 8 = 9 | too small | i+1 |
| 1 | 4 | 3 + 8 = 11 | too big | j-1 |
| 1 | 3 | 3 + 6 = 9 | too small | i+1 |
| 2 | 3 | 4 + 6 = 10 | equal | found |

Second call, `a = [2, 5, 9, 14]`, `target = 12`:

| i | j | a[i] + a[j] | compared with 12 | move |
|---|---|---|---|---|
| 0 | 3 | 2 + 14 = 16 | too big | j-1 |
| 0 | 2 | 2 + 9 = 11 | too small | i+1 |
| 1 | 2 | 5 + 9 = 14 | too big | j-1 |

Now `i = j = 1`, the loop stops, and the function returns `None`.

## Output

```
0 5 12 j-1
0 4 9 i+1
1 4 11 j-1
1 3 9 i+1
2 3 10 found
(2, 3)
0 3 16 j-1
0 2 11 i+1
1 2 14 j-1
None
```

## Key ideas

- Each step removes one element for good: 11 (too big even with the smallest value), then 1 (too small even with the
  largest remaining value), and so on. That is why the loop takes at most `n - 1` steps.
- The indices printed are 0-based; the found pair is values 4 and 6.
