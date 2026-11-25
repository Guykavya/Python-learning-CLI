## Hint 1

For each value, first write down which **Sales rows** survive the filters: a category filter keeps the rows of its products; a region filter keeps the rows of its stores; two filters keep the rows that satisfy both.

## Hint 2

For `COUNTROWS(Product)` with a store filter: in a single-direction model the store filter reaches `Sales` but stops there, so the product table is unfiltered. With a both-way relationship the filtered `Sales` rows filter `Product` back: only the products that were sold in the North remain.
