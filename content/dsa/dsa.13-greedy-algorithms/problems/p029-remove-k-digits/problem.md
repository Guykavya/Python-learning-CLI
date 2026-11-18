# Remove k digits

`num` is a string of digits (a non-negative integer with no leading zeros, or `"0"`). Remove **exactly** `k` digits so that the number that is left is as **small** as possible. Write `remove_k_digits(num, k)` that returns it as a string:

- with no leading zeros (`"0200"` is written `"200"`);
- `"0"` if nothing is left or only zeros are left.

The digits that stay keep their order.

## Example

```python
>>> remove_k_digits("1432219", 3)
'1219'
>>> remove_k_digits("10200", 1)      # remove the 1: "0200" -> "200"
'200'
>>> remove_k_digits("10", 2)         # nothing left
'0'
>>> remove_k_digits("12345", 2)      # digits only rise: remove from the right
'123'
```

## Constraints

- `1 <= len(num) <= 10**5`, `0 <= k <= len(num)`.
- `O(n)`: each digit pushed and popped at most once (chapter section 12).

## Think about

The leftmost digit matters most. If a digit is directly followed by a **smaller** digit, why is deleting it always right, whatever comes later? And what should happen to a digit that is followed by an **equal** digit?
