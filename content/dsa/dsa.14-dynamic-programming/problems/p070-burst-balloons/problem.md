# Burst balloons

A row of balloons carries numbers `nums`. When you burst balloon `i`, you earn `left * nums[i] * right` coins, where `left` and `right` are the numbers of its **current** neighbours (balloons already burst are gone, so neighbours change). A missing neighbour at either end counts as `1`. You burst all the balloons, in the order you choose.

Write `max_coins(nums)` that returns the **most** coins you can earn (chapter section 17).

## Example

```python
>>> max_coins([3, 1, 5, 8])
167
>>> max_coins([1, 5])          # burst 1 (1*1*5), then 5 (1*5*1)
10
>>> max_coins([7])
7
>>> max_coins([])
0
```

For `[3, 1, 5, 8]`: burst 1 (`3*1*5 = 15`), then 5 (`3*5*8 = 120`), then 3 (`1*3*8 = 24`), then 8 (`1*8*1 = 8`): `167`.

## Constraints

- `0 <= len(nums) <= 150`, `0 <= nums[i] <= 100`.
- `O(n^3)` time. Trying every order is `n!`; a recursion without a memo is exponential.

## Think about

If you choose the **first** balloon to burst, its two sides become neighbours of each other, so the left and right parts are no longer independent. Choose the **last** balloon `k` to burst inside a range instead. While it waits, what are its neighbours at the moment it finally bursts? Why are the parts on its left and on its right now independent?
