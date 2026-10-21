# One line of a receipt

Read three lines: an item name, a quantity (whole number) and a unit price (may have decimals). Print **one** receipt line made of four columns with no extra spaces between them:

| Column | Width | Rule |
|---|---|---|
| name | 15 | left-aligned; names longer than 15 characters are **cut** to 15 |
| quantity | 4 | right-aligned |
| price | 9 | right-aligned, 2 decimals |
| total | 11 | right-aligned, thousands separators, 2 decimals |

The total is quantity times price.

**Example**

Input:
```
Notebook
12
45.5
```
Output (the brackets are not printed; they show the edges):
```
[Notebook         12    45.50     546.00]
```

So the printed line is `Notebook         12    45.50     546.00`.
