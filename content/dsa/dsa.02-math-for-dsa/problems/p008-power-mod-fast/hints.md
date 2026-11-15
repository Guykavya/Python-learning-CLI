## Hint 1

`a^10 = (a^5)^2` and `a^5 = a * (a^2)^2`. What does the parity of the exponent tell you to do at each step?

## Hint 2

Keep a running `result` (start at 1) and a running `base` (start at `a % m`). Look at the lowest bit of `b`:
if it is 1, `result` needs one extra factor of `base`. Then `base` becomes `base * base` and `b` is shifted right.

## Hint 3

```
result = 1 % m
base = a % m
while b > 0:
    if b % 2 == 1: result = result * base % m
    base = base * base % m
    b //= 2
print result
```
