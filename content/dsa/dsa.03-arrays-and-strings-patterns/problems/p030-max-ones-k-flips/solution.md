## Approach

Rephrase first: "flip at most `k` zeros to get the longest run of ones" is the same as "find the longest subarray
with at most `k` zeros", because every zero inside the chosen run must be flipped and nothing outside it matters.

Then it is a variable window with a counter. The window `a[l..r]` keeps at most `k` zeros. Each new zero may push
the count over `k`; the window then drops elements from the left until a zero has left.

## Code

```python
n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

l = 0
zeros = 0            # zeros inside the window a[l..r]: the flips it needs
best = 0
for r in range(n):
    if a[r] == 0:
        zeros += 1
    while zeros > k:     # too many flips needed: shrink from the left
        if a[l] == 0:
            zeros -= 1
        l += 1
    if r - l + 1 > best:
        best = r - l + 1

print(best)
```

On the example with `k = 2` (positions 0-based): the window grows to `0..4` (zeros at 3 and 4). At `r = 5` the third
zero arrives, so `l` moves past positions 0, 1, 2 and the zero at 3: `l = 4`. The window `4..9` has zeros at 4 and 5
and length 6. At `r = 10` another zero arrives and `l` moves to 5, giving length 6 again.

## Complexity

O(n) time: `l` and `r` each move at most `n` times. O(1) extra memory.

## Another way

List the positions of the zeros: `z`. If there are at most `k` zeros, the answer is `n`. Otherwise every best run
uses `k` neighbouring zeros `z[i..i+k-1]` and stretches from just after `z[i-1]` to just before `z[i+k]` (use `-1`
and `n` as the outer edges). So the answer is the largest `z[i+k] - z[i-1] - 1`. Same O(n), but more index care.

A curious variant: replace the `while` by an `if`. The window then never gets shorter; when it holds too many
zeros it simply slides one step (both ends move). Its length is always the best length found so far, so printing
`r - l + 1` at the end, or tracking the maximum, still gives the right answer. It is a neat trick, but the
`while` version is easier to reason about, because its window is always valid.
