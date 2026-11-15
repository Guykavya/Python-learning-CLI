## Hint 1

Split the old intervals into three groups relative to the new one. What do the three groups look like?

## Hint 2

(1) intervals that end before `a` (`r < a`): copy. (2) intervals that start at or before `b` and end at or after `a`: absorb them into the new interval with `min` of starts and `max` of ends. (3) the rest (`l > b`): copy after.

## Hint 3

```
i = 0; out = []
while i < n and r[i] < a: out.append(iv[i]); i += 1
while i < n and l[i] <= b: a = min(a, l[i]); b = max(b, r[i]); i += 1
out.append((a, b))
while i < n: out.append(iv[i]); i += 1
```
