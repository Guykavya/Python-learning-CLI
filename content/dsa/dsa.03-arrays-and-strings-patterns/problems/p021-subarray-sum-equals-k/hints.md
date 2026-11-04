## Hint 1

Let `P[j]` be the sum of the first `j` elements (`P[0] = 0`). The sum of `a[i..j-1]` is `P[j] - P[i]`. So a
subarray ending just before position `j` has sum `k` when some earlier prefix equals what?

## Hint 2

When you reach prefix `P[j]`, you need the number of earlier prefixes equal to `P[j] - k`. A dictionary
`{prefix value: how many times it appeared}` answers that in O(1). Which prefix must be in the dictionary
**before** you read the first element, so that subarrays starting at index 0 are counted?

## Hint 3

```
seen = {0: 1}
prefix = 0, count = 0
for x in a:
    prefix += x
    count += seen.get(prefix - k, 0)     # look up first
    seen[prefix] += 1                    # then record (start from 0 if missing)
print count
```

Look up **before** you record the current prefix. Otherwise, for `k = 0`, each prefix matches itself and you
count an empty subarray at every step.
