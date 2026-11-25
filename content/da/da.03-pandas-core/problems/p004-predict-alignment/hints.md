## Hint 1

First write the labels of the result: the union of `a, b, c` and `b, c, d`, sorted. Then fill a table with the value of `a` and the value of `b` for each label (or "missing"). What is a number plus "missing"?

## Hint 2

```text
label   a    b     a + b    a.add(b, fill_value=0)
a       1    -     nan      1 + 0  = 1.0
b       2    10    12.0     2 + 10 = 12.0
c       3    20    23.0     3 + 20 = 23.0
d       -    30    nan      0 + 30 = 30.0
```
`a.values + b.values` forgets the labels: position 0 + position 0, and so on.
