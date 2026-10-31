## Hint 1

Write `a` and `b` as small tables first: `a = {b: 1, a: 3, n: 2}` (in insertion order), `b = {a: 1, n: 5, x: 2}`. Every other line is built from these two tables. For each operator ask: per letter, what number do I get, and is that number kept?

## Hint 2

The **operators** `+`, `-`, `&` (min) and `|` (max) keep only results that are **greater than zero**. The **method** `subtract()` keeps everything, zero and negative too, and adds keys it did not have. Unary `+c` throws away everything that is not positive.

## Hint 3

```
for each operator line:
    for each letter in a, then letters only in b:
        value = a[letter] OP b[letter]     # a missing letter counts as 0
        keep it only if value > 0
    print sorted by value, high to low, ties in insertion order
```
Reading `c["zzz"]` on a Counter returns 0 **without** adding the key. `update()` adds counts; `most_common(2)` breaks the tie at count 1 by insertion order.
