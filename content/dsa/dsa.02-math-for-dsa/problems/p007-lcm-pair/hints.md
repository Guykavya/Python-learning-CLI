## Hint 1

Take `a = 12` and `b = 18`. What is their gcd? What is `a * b`? How is the lcm related to those two numbers?

## Hint 2

`a * b` counts the common part twice. Dividing by the gcd removes the double count: `lcm = a * b // gcd`.
Which is better to compute first, `a * b` or `a // gcd`?

## Hint 3

```
g = gcd(a, b)           # Euclid loop
print(a // g * b)       # exact integer division, then multiply
```
