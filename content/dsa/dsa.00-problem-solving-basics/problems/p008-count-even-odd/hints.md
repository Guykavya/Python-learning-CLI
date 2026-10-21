## Hint 1

How can you tell if a number is even using `%`? Do you need to keep all the numbers, or only two counters?

## Hint 2

Read `c`, then loop `c` times. Inside the loop read one number and check `x % 2 == 0`. Increase the right counter. Print both counters after the loop, not inside it.

## Hint 3

```
even = 0
odd = 0
repeat c times:
    x = int(input())
    if x % 2 == 0: even += 1
    else: odd += 1
print("even", even)
print("odd", odd)
```
