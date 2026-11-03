## Approach

Group by equal `amount`: {10}, {20, 20}, {30, 30}, {40}.

- `dflt` (`RANGE`, peers included): sums at the end of each group: 10, 50, 50, 110, 110, 150. Both 20s show 50.
- `by_rows` (`ROWS`): 10, 30, 50, 80, 110, 150, in order of (amount, id), so id 2 gets 30 and id 3 gets 50.
- `cnt`: the number of rows up to the end of the group: 1, 3, 3, 5, 5, 6.
- `total`: no `ORDER BY` means the whole partition: 150 for every row.

## Code

```
1|10|10|10|1|150
2|20|50|30|3|150
3|20|50|50|3|150
4|30|110|80|5|150
5|30|110|110|5|150
6|40|150|150|6|150
```

## Complexity

Each window needs a sort of n rows. `RANGE` has to look ahead to find the end of the peer group; that costs no more than O(n) extra over the whole pass.

## Another way / portable SQL

The default frame is the same in PostgreSQL and MySQL 8. Always write `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` when you want a true running total, so ties and databases cannot surprise you.
