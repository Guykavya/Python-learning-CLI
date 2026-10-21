## Hint 1

If `d` divides `n`, what other number do you get for free? For `n = 36`, once you have reached `d = 6`,
have you already seen every divisor? Why?

## Hint 2

Start the sum at 1 (every `n > 1` has 1 as a proper divisor) and try `d = 2, 3, ...` while `d * d <= n`.
For each `d` that divides `n`, add `d` and also `n // d`, but only add `n // d` when it is different from `d`.
`n` itself is never added, because its partner 1 is handled by the starting value. Treat `n = 1` on its own.

## Hint 3

```
read n
total = 0 if n == 1 else 1
d = 2
while d * d <= n:
    if n % d == 0:
        total = total + d
        if n // d != d: total = total + n // d
    d = d + 1
compare total with n and print the word
```
