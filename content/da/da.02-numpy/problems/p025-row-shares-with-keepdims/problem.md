# Row shares with `keepdims`

Chapter sections 10.3 and 10.6. A table of sales has one row per shop and one column per product (all values
`>= 0`). Write `row_shares(x)` that returns a `float64` array of the same shape where each value is divided by **its
row's total**, so every row adds up to 1.

- A shop with no sales at all (a row of zeros) gets a row of zeros, **not** `nan`, and the function must not raise
  a RuntimeWarning (the tests turn warnings into errors).
- Integer input works. The input is not changed. No Python loops.

## Example

```python
x = np.array([[1, 2, 3],
              [0, 0, 0],
              [5, 0, 5]])
row_shares(x)
# array([[0.16666667, 0.33333333, 0.5       ],
#        [0.        , 0.        , 0.        ],
#        [0.5       , 0.        , 0.5       ]])
```
