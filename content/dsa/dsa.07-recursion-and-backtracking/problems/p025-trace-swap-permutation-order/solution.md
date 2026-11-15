## Approach

Use the structure. At level 0 the loop swaps position 0 with positions 0, 1, 2, 3 of the **original** list (each swap is undone before the next one), giving the starting lists `1234`, `2134`, `3214`, `4231`. For each, the last three digits `abc` follow the 3-item order `abc acb bac bca cba cab`.

## Expected output

```text
1234 1243 1324 1342 1432 1423
2134 2143 2314 2341 2431 2413
3214 3241 3124 3142 3412 3421
4231 4213 4321 4312 4132 4123
```

## Why

For `[a, b, c]` the swap method gives: `abc` (no swap), `acb` (swap the last two), then `bac` (swap a and b), `bca`, then `cba` (swap a and c), `cab`. The 5th entry is `cba`, not `cab`, because the swap of positions 0 and 2 exchanges a and c and leaves b in the middle.
Applied to line 3 with tail `2 1 4`: `214 241 124 142 412 421`. The output is **not** sorted (`3214` comes before `3124`). The `used`-list method on sorted input gives lexicographic order.
