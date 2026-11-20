## Hint 1

Write every number as 31 bits, highest first, and insert it into a trie whose nodes have at most two children, `0` and `1`. For a number `x`, the best partner differs from `x` on the highest possible bit: walk down from the top bit, and at every level go to the child **opposite** to `x`'s bit if it exists.

## Hint 2

A 1 in bit `b` of the XOR is worth `2**b`, more than `2**(b-1) + ... + 1`. So taking the opposite child whenever possible is always right (a greedy choice, dsa.13). If the opposite child is missing, you must take the same bit, and that bit of the XOR is 0.

## Hint 3

```
best = 0
insert(nums[0])
for x in nums[1:]:
    node, value = root, 0
    for b from 30 down to 0:
        bit = (x >> b) & 1
        if (1 - bit) in node: value |= 1 << b; node = node[1 - bit]
        else: node = node[bit]
    best = max(best, value)
    insert(x)
```
