# Months to a savings goal

Read three lines:

1. the savings goal in rupees (a whole number)
2. the deposit added at the end of every month (a whole number, 0 or more)
3. the monthly interest rate in percent (a number, 0 or more, may have decimals)

Start with a balance of 0. Each month, first add interest on the current balance
(`balance * rate / 100`), then add the deposit. Count the months until the balance is
**at least** the goal.

Print `Months: <m>` and `Balance: <balance with 2 decimals>`.

Special cases:

- If the goal is 0 or less, it is already reached: `Months: 0` and `Balance: 0.00`.
- If the deposit is 0 (and the goal is above 0), the balance stays 0 for ever. Print
  `Goal not reachable` instead of looping for ever.

**Example**

Input `1000`, `300`, `0`. Output:

```
Months: 4
Balance: 1200.00
```
