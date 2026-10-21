## Hint 1

A number divisible by both `a` and `b` is also divisible by `a` alone. If you check "divisible by `a`" first, will you ever reach the "both" case?

## Hint 2

Put the "both" check first: `i % a == 0 and i % b == 0`. Then check `a` alone, then `b` alone, then print the number. Use `if / elif / elif / else` so exactly one line is printed per `i`.

## Hint 3

```
for i in range(1, n + 1):
    if i % a == 0 and i % b == 0: print("FizzBuzz")
    elif i % a == 0: print("Fizz")
    elif i % b == 0: print("Buzz")
    else: print(i)
```
