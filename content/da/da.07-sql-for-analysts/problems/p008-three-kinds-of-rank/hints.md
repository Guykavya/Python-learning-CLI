## Hint 1

First sort the six orders by amount descending (and by `order_id` for ties) on paper. Number them 1 to 6: that is `row_number`. Which rows share the same amount?

## Hint 2

```text
sorted:  (2,500) (3,500) (6,400) (1,300) (4,200) (5,100)
rn       1 2 3 4 5 6                       -> never repeats
rk       tie shares the smaller position, next value skips ahead
dr       tie shares a number, next value is +1 (no gap)
half     6 rows in 2 groups -> first 3 rows are group 1, last 3 group 2
last line: the largest rk and the largest dr
```
