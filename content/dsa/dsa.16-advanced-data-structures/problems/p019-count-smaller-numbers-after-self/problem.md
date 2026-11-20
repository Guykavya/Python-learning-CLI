# Count smaller numbers after self

For a list of daily temperatures, a weather site shows next to each day how many **later** days were strictly colder. Write `smaller_after(nums)` that returns a list `out` with `out[i]` = the number of `j > i` with `nums[j] < nums[i]` (chapter section 12, "Variants").

## Example

```python
>>> smaller_after([5, 2, 6, 1])
[2, 1, 1, 0]
>>> smaller_after([-1, -1])
[0, 0]
>>> smaller_after([])
[]
```

For `5`: the later days `2` and `1` are colder. For `2`: only `1`. For `6`: only `1`.

## Constraints

- Up to 10**5 numbers from `-10**9` to `10**9`. `O(n log n)`.

## Think about

1. Scan from the **right**. When you reach `nums[i]`, what does the Fenwick tree contain, and which prefix gives the answer?
2. Equal values: are they "smaller"? Which rank do you query, `rank` or `rank + 1`?
3. How is the total of the list related to p018?
