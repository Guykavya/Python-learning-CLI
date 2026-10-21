# Exact fraction arithmetic

Read two fractions written like `1/3` (each on its own line). Using the `fractions` module, print:

1. their sum, as an exact fraction
2. their product, as an exact fraction
3. the sum converted to a `float`

**Example**

Input:
```
1/3
1/6
```
Output:
```
1/2
1/18
0.5
```

`Fraction` always keeps itself in lowest terms. If a result is a whole number, it prints
without a denominator, for example `1` instead of `1/1`.
