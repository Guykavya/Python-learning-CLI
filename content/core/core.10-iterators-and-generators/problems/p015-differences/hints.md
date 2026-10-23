## Hint 1

What are the pairs for `[1, 4, 9]`? How many pairs does a list of length n give?

## Hint 2

Loop over `pairwise(numbers)` and unpack each pair into `a, b`. Give `b - a`.

## Hint 3

```
return [b - a for a, b in pairwise(numbers)]
```
