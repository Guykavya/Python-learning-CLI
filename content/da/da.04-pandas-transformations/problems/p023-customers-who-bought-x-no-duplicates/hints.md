## Hint 1

First answer a smaller question: which customer ids appear on a line of this product? Then the result is "the
customers whose id is in that collection". Which method tests membership without repeating rows?

## Hint 2

```text
buyers = lines.loc[lines["product_id"] == product_id, "customer_id"]
result = customers[customers["customer_id"].isin(buyers)].reset_index(drop=True)
# merge version: merge with buyers.drop_duplicates() (inner), then keep the customer columns
```
