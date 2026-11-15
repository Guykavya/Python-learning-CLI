# Letter combinations of a phone number

On an old phone keypad each digit 2-9 stands for some letters:

```text
2: abc   3: def   4: ghi   5: jkl   6: mno   7: pqrs   8: tuv   9: wxyz
```

Write `letter_combinations(digits)` that returns all letter strings the digit string could mean, one letter per digit. For the empty string return `[]` (there is nothing to type). The order does not matter (the tests sort).

## Example

```python
>>> sorted(letter_combinations("23"))
['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']
>>> letter_combinations("")
[]
>>> len(letter_combinations("79"))
16
```

## Constraints

- `0 <= len(digits) <= 6`, only the characters `2` to `9`.
- Write the backtracking yourself; `itertools.product` is not allowed.

## Think about

How many answers are there for `"2345"`? (Multiply the sizes of the choices.) Why does `""` give `[]` here, while `binary_strings(0)` gave `[""]`?
