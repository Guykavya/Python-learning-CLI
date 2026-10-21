## Hint 1

Write 8 and 7 in binary. Write 6 and 5. What happens when you `&` each pair?

## Hint 2

Subtracting 1 flips the lowest 1 bit to 0 and all the 0 bits below it to 1. If that was the only
1 bit, nothing is left in common. Remember `==` binds tighter than `&`.

## Hint 3

```
print((n & (n - 1)) == 0)
print(n.bit_length())
print(1 << (n.bit_length() - 1))
```
