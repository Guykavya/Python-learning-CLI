## Approach

1. Category A = products 1 and 2: rows 1, 2, 3, 4, 7, 8 = 10 + 20 + 30 + 40 + 70 + 80 = **250**.
2. North = store 1: rows 1, 3, 4, 7 = 10 + 30 + 40 + 70 = **150**.
3. The Store filter does not flow to Product (single direction): all three products remain: **3**.
4. With the filter flowing both ways, the North rows (1, 3, 4, 7) use products 1 and 2: **2**.
5. Category A and North: rows 1, 3, 4, 7 = **150** (all North rows are products of A).

## Code

```text
250
150
3
2
150
```

## Complexity

Not applicable (a trace problem).

## Another way

Keep relationships single-direction and write a measure that counts the products with sales (`CALCULATE(DISTINCTCOUNT(Sales[ProductKey]))`): the same answer to "which products sold in the North" without the side effects of a both-way filter (problem 9).
