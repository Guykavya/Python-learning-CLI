# Three ways to round

Read a decimal number as text, for example `2.675`. Round it to 2 decimal places in three ways and print:

```
float round: <round(float(x), 2), shown with 2 decimals>
half up: <Decimal(x) rounded with ROUND_HALF_UP>
half even: <Decimal(x) rounded with ROUND_HALF_EVEN>
```

**Example**

Input:
```
2.675
```
Output:
```
float round: 2.67
half up: 2.68
half even: 2.68
```

Notice the first line: `2.675` as a float is really `2.67499999...`, so it rounds down.
