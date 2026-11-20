## Hint 1

Scan from right to left. Before handling `nums[i]`, the tree holds the counts per rank of all **later** numbers. The answer is how many of them have a rank **strictly smaller** than `nums[i]`'s rank: `prefix(rank)`.

## Hint 2

Compress: `ranks = {v: i for i, v in enumerate(sorted(set(nums)))}`. Query first, then `add(rank, 1)`.

## Hint 3

```
out = [0] * n
for i from n - 1 down to 0:
    k = ranks[nums[i]]
    out[i] = bit.prefix(k)
    bit.add(k, 1)
```
