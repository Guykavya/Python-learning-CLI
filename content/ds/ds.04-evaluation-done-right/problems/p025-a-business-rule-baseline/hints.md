## Hint 1

Turn each condition into 0/1 and multiply by its points. How do you compare a whole column with 3 at once?

## Hint 2

`2 * X['contract_month'] + 1 * (X['support_calls'] >= 3)`, as a float array.
