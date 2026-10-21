## Hint 1

If 36 = 4 x 9, one factor (4) is small and the other (9) is large. Can **both** factors of a number be larger than its square root?
What does that mean for how far you need to search?

## Hint 2

Try divisors `d = 2, 3, 4, ...` while `d * d <= n` (this avoids floats and square roots completely).
As soon as one divides `n`, you know the answer: stop. If none does, `n` is prime. Handle `n < 2` first.
Use `<=`, not `<`: for `n = 49` you must still try `d = 7`.

## Hint 3

```
read n
if n < 2: print "not prime" and stop
prime = True
d = 2
while d * d <= n:
    if n % d == 0:
        prime = False
        break
    d = d + 1
print "prime" if prime else "not prime"
```
