## Hint 1

Take `"Abcdefg1"`: it passes every rule. Now spoil exactly one rule at a time. What does the length rule's border look like: which lengths are 7, 8 and 9?

## Hint 2

For the digit rule: a password with upper, lower, length 8, no spaces, but no digit. Do the same for upper and lower. For the space rule: a password valid in every other way, with a space inside.

## Hint 3

```
test_valid: 'Abcdefg1' -> True
test_length_7: 'Abcdef1' -> False   # border
test_length_8_ok (above)
test_no_digit: 'Abcdefgh' -> False
test_no_upper: 'abcdefg1' -> False
test_no_lower: 'ABCDEFG1' -> False
test_space: 'Abcd efg1' -> False
```
