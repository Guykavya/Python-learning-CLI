# Draw a progress bar

Read two whole numbers: how many tasks are done, and the total (total is at least 1, and done is between 0 and total). Print a progress bar 20 characters wide, then the percentage with no decimals, then the counts:

```
[<filled with #><rest with ->] <percent>% (<done>/<total>)
```

The number of `#` characters is `done * 20 // total` (rounded down).

**Example**

Input:
```
1
3
```
Output:
```
[######--------------] 33% (1/3)
```
