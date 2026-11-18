# Jump game II

`nums[i]` is the maximum jump length from index `i`. You start at index 0, and the last index is **guaranteed** to be reachable. Write `min_jumps(nums)` that returns the **fewest jumps** needed to reach the last index (chapter section 11).

## Example

```python
>>> min_jumps([2, 3, 1, 1, 4])      # 0 -> 1 -> 4
2
>>> min_jumps([2, 3, 0, 1, 4])
2
>>> min_jumps([1, 1, 1, 1])
3
>>> min_jumps([0])                  # already there
0
```

## Constraints

- `1 <= len(nums) <= 10**5`, `0 <= nums[i] <= 10**5`, and the last index can always be reached.
- One pass, `O(n)`. A BFS that visits every index each jump can reach is correct but too slow when the jumps are long.

## Think about

Think of BFS in **layers**: layer 1 is every index reachable with 1 jump, layer 2 with 2 jumps, and so on. Why is every layer a block of consecutive indices? Then why do you only need to remember where the current layer ends?
