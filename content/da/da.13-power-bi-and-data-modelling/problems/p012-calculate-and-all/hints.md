## Hint 1

Which filter argument of `CALCULATE` sets `Product[Category]` to `"Kitchen"`? Does it add to the existing category filter or replace it? For the percentage, which function removes the filters of the `Product` table, and which function protects against a blank denominator?

## Hint 2

```text
"Kitchen revenue": 'CALCULATE([Revenue], Product[Category] = "Kitchen")'
"% of all revenue": "DIVIDE([Revenue], CALCULATE([Revenue], ALL(Product)))"
```
