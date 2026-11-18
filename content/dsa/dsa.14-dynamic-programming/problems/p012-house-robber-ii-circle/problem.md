# House robber II (circle)

The houses now stand in a **circle**: the first house and the last house are neighbours. Otherwise the rules of p011 hold: house `i` holds `nums[i]`, and you may not rob two adjacent houses. Write `rob_circle(nums)` that returns the most money you can take.

## Example

```python
>>> rob_circle([2, 3, 2])         # 2 and 2 are neighbours now: take the 3
3
>>> rob_circle([1, 2, 3, 1])      # 1 + 3
4
>>> rob_circle([2, 7, 9, 3, 1])   # 2 + 9 + 1 is no longer allowed (1 and 2 touch); 2 + 9 = 11, 7 + 3 = 10
11
>>> rob_circle([5])               # one house has no neighbour
5
```

## Constraints

- `1 <= len(nums) <= 10**5`, `0 <= nums[i] <= 400`.
- `O(n)` time.

## Think about

The circle has only **one** extra rule compared with the row: "not both the first and the last house". You already have a fast solution for a row. Can you split the circle problem into row problems by deciding something about the first or the last house?
