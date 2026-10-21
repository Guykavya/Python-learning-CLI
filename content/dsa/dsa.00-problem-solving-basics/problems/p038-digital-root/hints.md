## Hint 1

How do you know `n` "has one digit" using only a comparison, no string? What is the smallest number with two digits?

## Hint 2

Outer loop: `while n >= 10`. Inside it, compute the digit sum of `n` into a new variable with an inner loop
(`% 10` to get the last digit, `// 10` to drop it), then set `n` to that sum and add 1 to `rounds`.

## Hint 3

```
read n
rounds = 0
while n >= 10:
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    n = total
    rounds += 1
print "root", n
print "rounds", rounds
```

Note that `0` and `9` skip the outer loop completely.
