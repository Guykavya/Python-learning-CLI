# Count numbers ≤ N with a digit property: stepping numbers

A **stepping number** is a non-negative integer in which every two neighbouring digits differ by **exactly 1**. Every single-digit number (0 to 9) is a stepping number. `10`, `12`, `21`, `101`, `3210` and `78987` are stepping numbers; `11`, `13`, `100` and `1235` are not.

Write `count_stepping(lo, hi)` that returns how many integers `x` with `lo <= x <= hi` are stepping numbers. Use digit DP (chapter section 20).

## Example

```python
>>> count_stepping(0, 21)      # 0..9, 10, 12, 21
13
>>> count_stepping(10, 15)     # 10, 12
2
>>> count_stepping(90, 101)    # 98, 101
2
>>> count_stepping(0, 0)
1
```

## Constraints

- `0 <= lo <= hi <= 10**18`.
- Your function must answer in well under a second. Checking every number in the range is impossible for `hi = 10**18`.

## Think about

1. Build the number digit by digit from the left, as in chapter section 20. What must the state remember about the digits already placed to decide whether the next digit is allowed?
2. Write `100` as the fixed-length string `"100"` and `7` as `"007"`. Why would the leading zeros break the rule "neighbours differ by 1" for `7`? What extra flag fixes that (chapter section 20, "Leading zeros and the `started` flag")?
3. Your DP will most easily count the stepping numbers in `[0, N]`. How do you get `[lo, hi]` from that? What happens when `lo = 0`?
