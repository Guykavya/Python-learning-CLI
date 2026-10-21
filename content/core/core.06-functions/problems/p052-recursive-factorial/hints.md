## Hint 1

What is the simplest input, whose answer you know without any work?

## Hint 2

```
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
```
Check: is there a base case? Does each call get a smaller `n`? Assuming `factorial(n - 1)` is right, is `n * factorial(n - 1)` right?
