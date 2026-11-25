## Hint 1

Group the ten rows by country on paper and sort each group by amount, largest first (ties by `order_id` for the first query). Number the rows of each group 1, 2, 3... for `row_number`.

## Hint 2

```text
IN : 500(id 2), 500(id 4), 500(id 10), 300(id 1), 100(id 9)
US : 250(id 6), 250(id 7), 200(id 3)
UK : 400(id 8), 100(id 5)
row_number <= 2 : the first two rows of each group
rank <= 2       : rank 1 is shared by every tied top row; the next different value is rank 1 + (number tied)
```

The last line prints the number of rows kept by each query.
