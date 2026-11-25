## Hint 1

Which single NumPy call gives you all the numbers `0, 1, ..., n − 1` at once? What happens if you multiply that array by itself?

## Hint 2

```text
values = np.arange(n)            # int64: 0 .. n-1
squares = values * values         # element by element, in C
return int(squares.sum())         # one integer
```
