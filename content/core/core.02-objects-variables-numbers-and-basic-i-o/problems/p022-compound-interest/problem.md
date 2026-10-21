# Compound interest

Read four lines:

1. principal `P` (may have decimals)
2. yearly interest rate in percent `R` (may have decimals)
3. number of years `T` (whole number)
4. how many times per year interest is added `N` (whole number, at least 1)

The final amount is `A = P * (1 + R / (100 * N)) ** (N * T)`.

Print:

```
Amount: <A>
Interest: <A - P>
```

Both with a comma as thousands separator and 2 decimals (the `:,.2f` format spec).

**Example**

Input:
```
1000
10
5
1
```
Output:
```
Amount: 1,610.51
Interest: 610.51
```
