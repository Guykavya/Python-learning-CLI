## Hint 1

Do it by hand for 360 and keep a table: divisor, how many times it divides, what is left. Notice
that after removing all 2s and all 3s, a divisor like 4 or 6 can never divide what is left. So every
divisor that works is automatically prime. What should happen when the number left is itself a big prime?

## Hint 2

Let `m` be what is left. Try `d = 2, 3, 4, ...` only while `d * d <= m`: if `m` had a factor bigger
than its square root, it would also have one smaller, which you would already have removed. When the
loop ends, if `m > 1` then `m` is a prime factor (appearing once). For the output, keep a string
`result`; before adding a factor, add `" * "` if `result` is not empty.

## Hint 3

```
m = n; result = ""; d = 2
while d * d <= m:
    if m % d == 0:
        e = 0
        while m % d == 0: m //= d; e += 1
        if result != "": result += " * "
        result += d if e == 1 else d^e
    d += 1
if m > 1: add m the same way
print n = result
```
