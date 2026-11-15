# Next greater element in a circle

The numbers stand in a **circle**: after the last one comes the first one again. Write `next_greater_circular(nums)` that returns, for every position, the first number **strictly greater** than it when you walk forward around the circle (at most one full lap), or `-1` if there is none.

Chapter section 9, "Circular arrays": walk the indices `0 .. 2n - 1` and use `i % n`, so the second lap lets the last numbers find answers at the start. Push indices only during the first lap.

## Example

```python
>>> next_greater_circular([1, 2, 1])
[2, -1, 2]
>>> next_greater_circular([1, 2, 3, 4, 3])
[2, 3, 4, -1, 4]
>>> next_greater_circular([5, 5])
[-1, -1]
>>> next_greater_circular([])
[]
```

In `[1, 2, 1]` the last `1` walks around to the start and finds `2`. The `2` is the maximum, so nothing is greater.

## Constraints

- `0 <= len(nums) <= 10**5`. The tests compare with a slow version on 1,000 random lists and run one big list with a time limit.

## Think about

Which numbers always get `-1` in a circle? Why is pushing indices again on the second lap useless (and harmful for the stack size)?
