# Maximum XOR of two numbers

Write `max_xor(nums)` that returns the largest value of `a ^ b` over two entries `a`, `b` of the list (at different positions). A list with one number gives `0`. Use a **binary trie** over the bits of the numbers (chapter section 9).

## Example

```python
>>> max_xor([3, 10, 5, 25, 2, 8])     # 5 ^ 25 = 0b00101 ^ 0b11001 = 0b11100
28
>>> max_xor([0])
0
>>> max_xor([7, 7])
0
>>> max_xor([1, 2, 4, 8])             # 4 ^ 8 = 12
12
```

## Constraints

- `1 <= len(nums) <= 10**5`; `0 <= nums[i] < 2**31`.
- Trying every pair is `O(n**2)`: 5 * 10**9 pairs for the big test. Your function must run in `O(n * 31)`.

## Think about

1. Why is a 1 in bit 30 of the result worth more than all the lower bits together? What does that allow you to decide at the top of the trie?
2. For a number `x`, which child do you prefer at each level, and what if it is missing?
3. Insert first and query later, or query each number before inserting it? Does the order change the answer?
