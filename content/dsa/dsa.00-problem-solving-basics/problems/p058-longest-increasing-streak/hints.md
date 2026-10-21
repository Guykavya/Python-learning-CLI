## Hint 1

You cannot look back at old numbers, so decide now what to remember. When a new number arrives, what
do you need to know to decide whether the streak continues? And to report the answer at the end, what
must you have saved about the best streak?

## Hint 2

Keep `prev`, the current streak (`cur_start`, `cur_len`) and the best streak (`best_start`,
`best_len`). Read the first number before the loop. In the loop: if `x > prev` extend the streak,
otherwise start a new one at this position. Then compare with the best **every time** (not only when
the streak breaks), using `>` so the earliest streak wins ties. Do not forget `prev = x`.

## Hint 3

```
prev = first value; cur_start = 1; cur_len = 1; best_start = 1; best_len = 1
for pos in 2..n:
    x = next value
    if x > prev: cur_len += 1
    else: cur_start = pos; cur_len = 1
    if cur_len > best_len: best_len = cur_len; best_start = cur_start
    prev = x
print "length", best_len
print "from", best_start, "to", best_start + best_len - 1
```
