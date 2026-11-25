## Hint 1

Which function keeps only one column's filter? What does the denominator look like for a visual row "Kitchen / Product 05": the revenue of the whole Kitchen category in the same year and region.

## Hint 2

```text
"% of category": "DIVIDE([Revenue], CALCULATE([Revenue], ALLEXCEPT(Product, Product[Category])))"
```
