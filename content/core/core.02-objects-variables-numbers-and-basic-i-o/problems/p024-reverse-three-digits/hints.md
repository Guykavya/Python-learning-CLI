## Hint 1

How do you get the hundreds digit of 123? The ones digit?

## Hint 2

Once you have the three digits, the reversed number is a weighted sum. Which digit gets the weight 100?

## Hint 3

```
hundreds = n // 100
tens = n // 10 % 10
ones = n % 10
rev = ones * 100 + tens * 10 + hundreds
```
