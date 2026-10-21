## Hint 1

If you had the reverse of `n` as a number, how would you decide the answer in one comparison?

## Hint 2

Reuse the reverse-number loop: `rev = rev * 10 + n % 10`, then `n //= 10`. But that loop shrinks `n` down to 0, so save a copy of the original value before the loop and compare `rev` with the copy afterwards. Deal with negatives before anything else.

## Hint 3

```
if n < 0: print no
else:
    original = n
    rev = 0
    while n > 0:
        rev = rev * 10 + n % 10
        n = n // 10
    if rev == original: yes else no
```
