# Shop bill with exact tax

Read three lines:

1. the unit price, like `19.99`
2. the quantity, a whole number
3. the tax rate in percent, like `18` or `12.5`

Print:

```
Subtotal: <price * quantity>
Tax: <subtotal * rate / 100>
Total: <subtotal + tax>
```

All three amounts must have exactly 2 decimal places. Round the tax to the nearest
cent (paisa) with **halves rounded up** (0.005 becomes 0.01), as shops do.
Use the `decimal` module so that no binary rounding errors creep in.

**Example**

Input:
```
19.99
2
18
```
Output:
```
Subtotal: 39.98
Tax: 7.20
Total: 47.18
```
