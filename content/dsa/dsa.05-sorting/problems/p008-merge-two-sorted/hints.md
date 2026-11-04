## Hint 1

Imagine two queues of people sorted by height. Who is next in the merged line? How many people do you have to look at to decide?

## Hint 2

Keep `i` in the first list and `j` in the second. Compare `a[i]` and `b[j]`, take the smaller, advance that pointer. When one list ends, copy the rest of the other.

## Hint 3

```
i = j = 0; out = []
while i < n and j < m:
    if a[i] <= b[j]: out.append(a[i]); i += 1
    else: out.append(b[j]); j += 1
out += a[i:]; out += b[j:]
```
