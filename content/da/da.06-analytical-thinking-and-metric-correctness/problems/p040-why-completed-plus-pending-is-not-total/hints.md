## Hint 1

For each of the three dashboard numbers, ask two questions: *which date* places a job in February, and *which
statuses* are allowed? Compare the answers for the total and for the parts. Then ask what the `started_at` of a pending
job is, and what a filter on a missing date returns.

## Hint 2

```text
total: created in Feb, all statuses | parts: started in Feb, status completed or pending
bigger parts: created in January, started in Feb (+98)
smaller parts: started in March (-87), cancelled (-84), failed (-13)
pending: no start date -> never selected -> exactly 0
net: -87 - 84 - 13 + 98 = -86 (four flows, not one)
fix: one date basis + all statuses; and a bridge with a reason and ids per line
```
Write one short paragraph for each numbered question.
