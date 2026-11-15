## Approach

Run the loop by hand with `i` and `j`. Every swap puts a small value into the small zone. The last step swaps the pivot into its final place.

## Expected output

```text
j = 0 i = 0 [7, 2, 9, 4, 3, 8, 5]
j = 1 i = 1 [2, 7, 9, 4, 3, 8, 5]
j = 2 i = 1 [2, 7, 9, 4, 3, 8, 5]
j = 3 i = 2 [2, 4, 9, 7, 3, 8, 5]
j = 4 i = 3 [2, 4, 3, 7, 9, 8, 5]
j = 5 i = 3 [2, 4, 3, 7, 9, 8, 5]
pivot index 3 [2, 4, 3, 5, 9, 8, 7]
j = 0 i = 0 [4, 4, 4, 4]
j = 1 i = 0 [4, 4, 4, 4]
j = 2 i = 0 [4, 4, 4, 4]
0 [4, 4, 4, 4]
```

## Why

For the first list the pivot 5 ends at index 3 with `[2, 4, 3]` on its left and `[9, 8, 7]` on its right (not sorted inside). For equal values the pivot index is the first position: the left part is empty and the right part has `n - 1` elements, the worst case. This is why quick sort needs a better partition (three-way) or a random pivot on inputs with many duplicates.
