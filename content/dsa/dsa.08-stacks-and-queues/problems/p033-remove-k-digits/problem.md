# Remove k digits

`num` is a string of digits (a non-negative number without leading zeros, or `"0"`). Remove **exactly** `k` digits so that the number formed by the remaining digits, in their original order, is as **small** as possible. Write `remove_k_digits(num, k)` and return the result as a string:

- without leading zeros (`"0200"` becomes `"200"`);
- `"0"` if nothing (or only zeros) is left.

Greedy idea (chapter section 10, "Remove k digits"): scanning from the left, a digit that is **larger than the digit after it** should go, because the smaller digit then moves into a more important position. Keep an **increasing** stack of digits; pop while the top is larger than the new digit and removals are left.

## Example

```python
>>> remove_k_digits("1432219", 3)
'1219'
>>> remove_k_digits("10200", 1)
'200'
>>> remove_k_digits("10", 2)
'0'
>>> remove_k_digits("112", 1)
'11'
```

## How it is tested

Fixed cases for the three edge cases (removals left over at the end, leading zeros, empty result) and 1,000 random cases compared with trying every way to remove `k` digits.

## Constraints

- `1 <= len(num) <= 10**5`, `0 <= k <= len(num)`.

## Think about

After the scan, removals may be left over (`"112"`, `k = 1`). The stack is increasing then: which digits should go?
