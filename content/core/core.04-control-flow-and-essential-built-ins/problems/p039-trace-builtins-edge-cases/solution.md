## Walkthrough

| Line | Output | Why |
|---|---|---|
| 1 | `False True` | nothing is true; nothing is false |
| 2 | `False True` | all three are falsy; `[0]` is a non-empty list, so truthy |
| 3 | `0 20` | sum of nothing is 0; 0+1+2+3+4 = 10, plus start 10 |
| 4 | `2` | `True` counts as 1 |
| 5 | `apple Banana` | `"a"` > `"B"` in character codes; with `str.lower`, `"banana"` > `"apple"` |
| 6 | `3 -7` | compared by distance from 0, returns the original numbers |
| 7 | `none` | empty with a default |
| 8 | `e` | smallest character of `"hello"` |
| 9 | `bb` | `bb` and `cc` tie on length; first wins |
| 10 | `4 4.0` | equal values: the first argument is returned |
| 11 | `True False` | `all` of nothing vs. the string method's "not empty" rule |
| 12 | `empty range` | `range(0)` is falsy, so `max` is never called |
