## Hint 1

The best subarray either stays inside the array (no wrap), or it wraps around the end. The first case is plain
Kadane. In the second case, the elements **not** taken form one ordinary subarray in the middle. What must be
true of that middle part if the wrapping part is as large as possible?

## Hint 2

Wrapping sum = `total - (sum of the middle part)`. To make it largest, the middle part must be the **smallest**
subarray sum: run Kadane with `min` instead of `max`. Answer = `max(best_max, total - best_min)`. What goes wrong
when every element is negative? (Then `best_min` is the whole array.)

## Hint 3

```
cur_max = best_max = a[0]; cur_min = best_min = a[0]
for x in a[1:]:
    cur_max = max(x, cur_max + x); best_max = max(best_max, cur_max)
    cur_min = min(x, cur_min + x); best_min = min(best_min, cur_min)
if best_max < 0: print best_max
else: print max(best_max, sum(a) - best_min)
```
