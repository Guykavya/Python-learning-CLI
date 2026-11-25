## Hint 1

Write the labels `a b c d` with positions `0 1 2 3` under them. For `loc`, both named labels are in. For `iloc`, the end position is out. Each slice has a rows part and a columns part: which one is it changing?

## Hint 2

```text
labels  a  b  c  d        columns x y z (positions 0 1 2)
pos     0  1  2  3
loc["b":"d"]        rows b,c,d (d included)      -> (3, 3)
iloc[1:3]           rows at 1,2 (3 excluded)     -> (2, 3)  b, c
loc[:, "x":"z"]     all rows, columns x,y,z      -> (4, 3)
iloc[:, 1:]         all rows, columns from 1 on  -> (4, 2)  y, z
```
