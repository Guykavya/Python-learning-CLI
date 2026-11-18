# Largest number from an array

Given a list of non-negative integers, arrange them so that, written one after another, they form the **largest** possible number. Write `largest_number(nums)` that returns that number **as a string** (it may be far too long for any fixed-size integer type).

The answer has no leading zeros: `[0, 0]` gives `"0"`, not `"00"`.

## Example

```python
>>> largest_number([10, 2])
'210'
>>> largest_number([3, 30, 34, 5, 9])
'9534330'
>>> largest_number([0, 0])
'0'
>>> largest_number([121, 12])
'12121'
```

## Constraints

- `1 <= len(nums) <= 1000`, `0 <= nums[i] <= 10**9`.
- Do not change the caller's list.

## Think about

Sorting the numbers as text in descending order puts `"30"` before `"3"` and gives `9534303`. Why is that wrong, and which quantity should the comparison look at instead? Chapter section 12 answers it; also think about why the rule must be **transitive** for a sort to use it.
