## Hint 1

What is the only visible difference between a list comprehension and a generator expression? What does that difference change about *when* the work happens?

## Hint 2

Start from `[n * n for n in numbers]` and replace the square brackets.

## Hint 3

```
return (n * n for n in numbers)
```
