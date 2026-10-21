## Hint 1

If 91 = 7 * 13, you find the divisor 7 before you ever reach 13. If `x` has any divisor other than 1 and `x`,
must it have one that is at most the square root of `x`? Try `x = 36`, `x = 35` and `x = 49`.

## Hint 2

Divisors come in pairs `d` and `x // d`. The smaller one of each pair satisfies `d * d <= x`. So try
`d = 2, 3, 4, ...` while `d * d <= x` and stop at the first divisor you find. Use `<=`, not `<`:
for `x = 25` the only small divisor is 5, and `5 * 5` equals 25.

## Hint 3

```
read n
count = 0, line = empty text
for x from 2 to n:
    is_prime = True
    d = 2
    while d * d <= x:
        if x % d == 0: is_prime = False, break
        d += 1
    if is_prime: add x to line (with a space before it if line is not empty), count += 1
if count > 0: print line
print "count", count
```

Bonus speed-up: after checking 2, only odd numbers can be prime, and only odd divisors need testing.
