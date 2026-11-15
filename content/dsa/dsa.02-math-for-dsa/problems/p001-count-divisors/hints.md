## Hint 1

How can you test, with one operator, whether `d` divides `n` exactly? What does `n % d` give when it does?

## Hint 2

Which values of `d` can possibly be divisors? Is 0 allowed? Is `n` itself a divisor?

## Hint 3

```
read q
repeat q times:
    read n
    count = 0
    for d from 1 to n (inclusive):
        if n % d == 0: count += 1
    print count
```
