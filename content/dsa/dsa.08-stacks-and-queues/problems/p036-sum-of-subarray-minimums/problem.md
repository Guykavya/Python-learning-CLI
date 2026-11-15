# Sum of subarray minimums

For a list `arr` of positive integers, consider **every** subarray (contiguous, non-empty). Write `sum_subarray_mins(arr)` that returns the sum of the minimums of all subarrays, **modulo `10**9 + 7`**.

There are `n (n + 1) / 2` subarrays, so listing them is far too slow for `n = 10**5`. Use the **contribution technique** (chapter section 10): for each `arr[i]`, count the subarrays in which it is the minimum.

- `p` = index of the previous element that is **strictly smaller** (or `-1`);
- `q` = index of the next element that is **smaller or equal** (or `n`);
- then `arr[i]` is the minimum of exactly `(i - p) * (q - i)` subarrays.

The asymmetric rule (strict on one side, not strict on the other) makes sure that a subarray with several equal minimums is counted **once**.

## Example

```python
>>> sum_subarray_mins([3, 1, 2, 4])
17
>>> sum_subarray_mins([11, 81, 94, 43, 3])
444
>>> sum_subarray_mins([2, 2])
6
```

`[3, 1, 2, 4]`: the subarrays have minimums 3, 1, 2, 4, 1, 1, 2, 1, 1, 1, which add up to 17. `[2, 2]`: `[2]`, `[2]` and `[2, 2]` give 2 + 2 + 2 = 6 (the pair counts once, not twice).

## How it is tested

1,000 random lists with many repeated values compared with a brute force, and two lists of 100,000 numbers with a time limit, where the answer is far above `10**9 + 7`.

## Constraints

- `1 <= len(arr) <= 10**5`, `1 <= arr[i] <= 3 * 10**4`.

## Think about

With `[2, 2]`, what goes wrong if both sides use "strictly smaller"? And if both use "smaller or equal"?
