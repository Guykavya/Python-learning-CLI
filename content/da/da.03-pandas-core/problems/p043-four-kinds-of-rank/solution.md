## Approach

Sort first, give positions, then work out the tied groups.

`s = [3, 1, 3, 2]`: sorted `1, 2, 3, 3`. The value 1 is first, 2 is second, and the two 3s take positions 3 and 4.

- `average`: the 3s share 3 and 4, so 3.5 each: `[3.5, 1.0, 3.5, 2.0]`.
- `min`: both get 3: `[3.0, 1.0, 3.0, 2.0]`.
- `dense`: the ranks are 1, 2, 3 for the three distinct values: `[3.0, 1.0, 3.0, 2.0]` (the same as `min` here, because nothing comes after the tie).
- `first`: ties are split in order of appearance: the first 3 is third, the second is fourth: `[3.0, 1.0, 4.0, 2.0]`.

`t = [30, 10, 30, 20, 10]`, sorted `10, 10, 20, 30, 30`. With `max`, the 10s get 2, the 20 gets 3, the 30s get 5: `[5.0, 2.0, 5.0, 3.0, 2.0]`. With `min` and `ascending=False` the 30s take positions 1 and 2 (both get 1), the 20 is third and the 10s take 4 and 5 (both get 4): `[1.0, 4.0, 1.0, 3.0, 4.0]`.

Finally every `rank` result is a float, even for integer data and even for `first`: `float64 float64`.

## Code

The expected output is in `expected.txt`, produced by running the program above.

## Complexity

`rank` sorts, so it is O(n log n) for each call.

## Another way

`min` is the "competition ranking" (1, 1, 3), `dense` is the "no gaps" ranking (1, 1, 2), `first` is the one to use when you need every row to have a **different** rank (for example to pick the top n per group later). If the result must be integers, `astype(int)` is safe only when there is no NaN (ranks of missing values are NaN).
