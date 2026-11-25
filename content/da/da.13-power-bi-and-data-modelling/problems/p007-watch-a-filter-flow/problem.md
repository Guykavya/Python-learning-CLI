# Watch a filter flow

Chapter sections 4.1 to 4.5. A filter set on a **dimension** flows **down** the relationship to the fact table (single direction): selecting a category filters the sales, but selecting a store does **not** filter the product table, unless the relationship is set to filter in **both** directions.

The model has three tables. `Revenue = SUM(Sales[Amount])`.

| Product: ProductKey | Category |
|---|---|
| 1 | A |
| 2 | A |
| 3 | B |

| Store: StoreKey | Region |
|---|---|
| 1 | North |
| 2 | South |

| Sales row | ProductKey | StoreKey | Amount |
|---|---|---|---|
| 1 | 1 | 1 | 10 |
| 2 | 1 | 2 | 20 |
| 3 | 2 | 1 | 30 |
| 4 | 2 | 1 | 40 |
| 5 | 3 | 2 | 50 |
| 6 | 3 | 2 | 60 |
| 7 | 1 | 1 | 70 |
| 8 | 2 | 2 | 80 |

Relationships: `Sales[ProductKey] -> Product[ProductKey]` and `Sales[StoreKey] -> Store[StoreKey]` (many-to-one, **single** direction), unless stated otherwise. Work out these five values and write them, **one per line, in this order**, in `answer.txt` (whole numbers):

1. `Revenue` with the filter `Product[Category] = "A"`;
2. `Revenue` with the filter `Store[Region] = "North"`;
3. `COUNTROWS(Product)` with the filter `Store[Region] = "North"` (single direction);
4. the same `COUNTROWS(Product)` with the filter `Store[Region] = "North"`, but with the relationship `Sales -> Product` set to filter in **both** directions;
5. `Revenue` with both filters, `Product[Category] = "A"` **and** `Store[Region] = "North"`.

## Example

`Revenue` with the filter `Store[Region] = "South"` is `20 + 50 + 60 + 80 = 210`.
