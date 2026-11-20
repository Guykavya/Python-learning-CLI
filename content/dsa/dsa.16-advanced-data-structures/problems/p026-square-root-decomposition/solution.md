## Approach

Chapter section 16. Blocks of size `B` keep their sums. A query adds single elements up to the first block boundary, whole blocks in the middle, and single elements after the last whole block. An update fixes one element and one block sum.

```python
import math


class BlockSum:
    def __init__(self, a):
        self.a = list(a)
        self.n = len(a)
        self.B = max(1, math.isqrt(self.n))
        nb = (self.n + self.B - 1) // self.B
        self.blocks = [sum(self.a[b * self.B:(b + 1) * self.B]) for b in range(nb)]

    def update(self, i, v):
        self.blocks[i // self.B] += v - self.a[i]
        self.a[i] = v

    def query(self, l, r):
        a, blocks, B = self.a, self.blocks, self.B
        total = touched = 0
        while l < r and l % B != 0:           # left partial block, one by one
            total += a[l]
            l += 1
            touched += 1
        while l + B <= r:                     # whole blocks
            total += blocks[l // B]
            l += B
            touched += 1
        while l < r:                          # right partial block
            total += a[l]
            l += 1
            touched += 1
        return total, touched
```

## Complexity

Build `O(n)`; update `O(1)`; query at most `(B - 1) + n / B + (B - 1)` steps, `O(sqrt n)` with `B = sqrt n`. That is slower than the `O(log n)` trees, but the blocks can hold **anything**, for example a sorted list per block to count elements `>= x` (chapter section 16), which no simple tree can merge.

## Another way

Store prefix sums inside each block too, so a partial block is one subtraction instead of a loop: queries become `O(n / B)` with `O(B)` updates. Choosing the block size balances update and query costs.
