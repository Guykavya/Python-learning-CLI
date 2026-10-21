## Hint 1

For `n = 4`, how many spaces and how many stars are on rows 1, 2, 3 and 4? Write the numbers in a table.
What happens to each count when you go down one row?

## Hint 2

Spaces go down by 1 each row and stars go up by 2 each row. Row `i` has `n - i` spaces and `2 * i - 1` stars.
You can build each row with string repetition instead of an inner loop.

## Hint 3

```
read n
for i from 1 to n (inclusive):
    print (n - i) spaces followed by (2*i - 1) stars, on one line
```

`range(1, n + 1)` gives 1 to n. For `n = 0` the loop runs zero times, which prints nothing.
