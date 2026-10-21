## Hint 1

What is `13 % 2`, then `13 // 2`? Keep going until the number is 0. Write the remainders down.
They are the base-2 digits, but in which order? Which digit does `% b` give you: the first or the last?

## Hint 2

Plan the special cases before the loop: an invalid base, `n == 0` (the loop would run zero times
and print nothing), and negative `n` (remember a `-` sign, then work with `abs(n)`, because `%` with
negatives behaves differently). Since the digits come out last-first, put each new character in front:
`result = DIGITS[d] + result`.

## Hint 3

```
read n, b
DIGITS = "0123456789ABCDEF"
if b < 2 or b > 16: print "invalid base"
elif n == 0: print "0"
else:
    sign = "-" if n < 0 else ""
    m = abs(n)
    result = ""
    while m > 0:
        result = DIGITS[m % b] + result
        m //= b
    print sign + result
```
