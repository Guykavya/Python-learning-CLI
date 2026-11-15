# Range sum queries

You get an array and many questions of the form "what is the sum of the elements from position `l` to position `r`?".
Positions are **1-based** and the range is **inclusive**: `l = 2, r = 4` means the 2nd, 3rd and 4th elements.

With up to 200000 elements and 200000 questions, adding the elements of each range one by one is far too slow.
Build the prefix sums once (`p[0] = 0`, `p[i]` = sum of the first `i` elements). Then

```
sum of positions l..r = p[r] - p[l-1]
```

answers each question with one subtraction.

## Input

- Line 1: `n`.
- Line 2: `n` integers.
- Line 3: `q`, the number of questions.
- Next `q` lines: two integers `l r`.

## Output

`q` lines, the answer to each question in order.

## Example

Input:

```
6
2 7 -3 5 1 4
4
2 4
1 6
3 3
5 6
```

Output:

```
9
16
-3
5
```

`7 + (-3) + 5 = 9`. The whole array sums to 16. The range `3..3` is the single element `-3`.

## Constraints

- `1 <= n, q <= 200000`
- `-10^9 <= a[i] <= 10^9`
- `1 <= l <= r <= n`

Read input with `input()`. (Reading 200000 lines with `input()` is fast enough.)
