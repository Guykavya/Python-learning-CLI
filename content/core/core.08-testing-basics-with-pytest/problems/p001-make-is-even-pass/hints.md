## Hint 1

Look at the first failure. pytest prints the line with the `assert` and the values on both sides. What did `is_even(4)` return, and what should it be?

## Hint 2

The function currently tests for remainder 1. What is `4 % 2`? What is `-3 % 2` in Python (chapter 2 told you how `%` treats negatives)?

## Hint 3

```
return n % 2 == 0
```
