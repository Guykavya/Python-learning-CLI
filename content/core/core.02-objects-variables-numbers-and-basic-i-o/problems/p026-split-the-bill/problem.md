# Split a bill fairly

Read a bill total in rupees with up to 2 decimal places (like `100` or `250.75`), then the
number of people. Each person pays the same whole number of paise (1 rupee = 100 paise),
as much as possible. Print:

```
Each pays: <rupees with 2 decimals>
Left over paise: <paise that could not be split evenly>
```

Work in whole paise using `int`. Convert the input with `Decimal`, not `float`.

**Example**

Input:
```
100
3
```
Output:
```
Each pays: 33.33
Left over paise: 1
```
