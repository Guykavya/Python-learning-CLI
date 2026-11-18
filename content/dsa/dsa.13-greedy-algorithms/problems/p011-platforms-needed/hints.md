## Hint 1

The number of platforms in use only changes when a train arrives (+1) or leaves (-1). The answer is the **highest** value this count ever reaches. Does it matter **which** train leaves at 1120, or only **that** a train leaves at 1120?

## Hint 2

Sort the arrivals and the departures separately. Walk with two indices, like the merge step of merge sort: at each step take the earlier of the next arrival and the next departure. When the times are equal, the chapter says the departure goes first, so treat the arrival as "next" only when `arr[i] < dep[j]` (strictly). You can stop when all arrivals are done: the remaining departures only lower the count.

## Hint 3

```
arr = sorted(arrivals); dep = sorted(departures)
i = j = 0; count = best = 0
while i < n:
    if arr[i] < dep[j]:  count += 1; best = max(best, count); i += 1
    else:                count -= 1; j += 1
return best
```
