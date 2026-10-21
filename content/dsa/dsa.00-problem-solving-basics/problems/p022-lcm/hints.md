## Hint 1

Any number that divides both `a` and `b` also divides `a % b` (the remainder). So what is the link between
`gcd(a, b)` and `gcd(b, a % b)`? What is `gcd(x, 0)`?

## Hint 2

Copy `a` and `b` into two new variables (you still need the originals for the LCM). Repeat
`x, y = y, x % y` while `y` is not 0; then `x` is the GCD. Finally compute the LCM with `//`, never `/`.

## Hint 3

```
read a, b
x = a, y = b
while y != 0:
    x, y = y, x % y
g = x
print (a // g) * b
```
