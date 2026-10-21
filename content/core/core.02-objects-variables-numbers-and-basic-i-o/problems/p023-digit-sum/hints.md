## Hint 1

Run the starter with `-4071`. Why is the answer wrong? What does `-4071 % 10` give?

## Hint 2

Make the number non-negative first with `abs()`. Then the ones digit is `n % 10`, the tens digit
is `n // 10 % 10`, and so on.

## Hint 3

```
n = abs(int(input()))
total = n % 10 + n // 10 % 10 + n // 100 % 10 + n // 1000 % 10
print(total)
print(total % 3 == 0)
```
