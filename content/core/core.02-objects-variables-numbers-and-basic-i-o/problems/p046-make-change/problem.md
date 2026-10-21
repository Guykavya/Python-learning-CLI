# Notes and coins for an amount

Read an amount in rupees with up to 2 decimals, like `1234.75`. Break it into the fewest
notes and coins of 500, 100, 50, 10, 5 and 1 rupees, always taking as many of the largest
as possible. What is left (below 1 rupee) is paise.

Print exactly these seven lines:

```
500: <count>
100: <count>
50: <count>
10: <count>
5: <count>
1: <count>
paise: <count>
```

**Example**

Input:
```
1234.75
```
Output:
```
500: 2
100: 2
50: 0
10: 3
5: 0
1: 4
paise: 75
```

Work in whole paise with `int`, and use `divmod` at each step. Read the input with `Decimal`.
