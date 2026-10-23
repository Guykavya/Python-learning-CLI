## Hint 1

What makes a function a generator function? Which keyword must appear in its body? What do you do with a loop variable that you want to hand to the caller one at a time?

## Hint 2

Use a `while` loop (or a `range` with a negative step). Instead of `append`, write `yield`. Nothing at the end: the function simply runs off its end and Python raises `StopIteration` for you.

## Hint 3

```
def countdown(n):
    while n > 0:
        yield n
        n -= 1
```
