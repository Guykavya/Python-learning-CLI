# Fix the canteen receipt

A classmate wrote a receipt printer for the college canteen. It should print:

```
Canteen receipt
Item: Samosa
Quantity: 3
Total: Rs 45
Thank you!
```

It crashes. There are **three** separate bugs. Fix them one at a time:

1. Run `python3 solution.py`.
2. Read the **last line** of the error (type and message) and the **line
   number**.
3. Fix only that line. Run again.

Rules: keep the variables. The total must still be calculated as
`price * quantity` (do not type `45`).

**Example**

Output after all fixes:
```
Canteen receipt
Item: Samosa
Quantity: 3
Total: Rs 45
Thank you!
```
