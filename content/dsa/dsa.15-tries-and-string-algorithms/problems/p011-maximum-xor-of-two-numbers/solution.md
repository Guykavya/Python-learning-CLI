## Approach

Chapter section 9. Insert the numbers bit by bit, highest bit first, into a binary trie (each node has the children `0` and `1`, stored here as dict keys). For each number `x`, walk down and prefer the child **opposite** to `x`'s bit.

Why greedy per bit is correct: a 1 in bit `b` of the XOR is worth `2**b`, which is more than all lower bits together (`2**b > 2**b - 1`). So whenever the current bit can be 1, any choice that makes it 0 is worse, whatever happens below.

```python
BITS = 31


def max_xor(nums):
    root = {}

    def insert(x):
        node = root
        for b in range(BITS - 1, -1, -1):
            node = node.setdefault((x >> b) & 1, {})

    def best_partner(x):
        node, value = root, 0
        for b in range(BITS - 1, -1, -1):
            bit = (x >> b) & 1
            want = 1 - bit                     # the opposite bit gives a 1 in the XOR
            if want in node:
                value |= 1 << b
                node = node[want]
            else:
                node = node[bit]               # forced to match: this XOR bit is 0
        return value

    best = 0
    insert(nums[0])
    for x in nums[1:]:
        best = max(best, best_partner(x))
        insert(x)
    return best
```

Querying each number **before** inserting it compares every pair exactly once (each number with all earlier ones) and never pairs a number with itself. Inserting everything first and then querying also works: pairing `x` with itself gives `x ^ x = 0`, which can never beat the best real pair, and when there is only one number the answer is 0 anyway.

## Complexity

`O(n * 31)` time and at most `n * 31` trie nodes. For `n = 10**5` that is about 3 million steps.

## Another way

Build the answer bit by bit with a set (no trie): for `b` from 30 down, guess that bit `b` of the answer is 1 (`candidate = answer | 1 << b`), put the top bits of every number (`x >> b`) in a set, and check whether two prefixes XOR to `candidate >> b` (for each prefix `p`, is `p ^ (candidate >> b)` in the set?). Keep the bit if yes. Also `O(n * 31)`, and often faster in Python because sets are implemented in C.
