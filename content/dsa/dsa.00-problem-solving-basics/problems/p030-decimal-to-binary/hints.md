## Hint 1

What is `n % 2`, and which binary digit of `n` does it give you: the leftmost or the rightmost?
What does `n // 2` do to the binary form of `n`?

## Hint 2

Each `n % 2` gives the next digit **from the right**. So build the answer by putting each new digit in front:
`result = str(bit) + result`. Stop when `n` reaches 0. Think about what this loop does for `n = 0`.

## Hint 3

```
read n
if n == 0: print "0"
else:
    result = ""
    while n > 0:
        result = str(n % 2) + result
        n = n // 2
    print result
```
