# Best day to buy and sell

`prices[i]` is the price of a share on day `i`. You may buy **one** share on one day and sell it on a **later** day.
Print the largest profit you can make. If no trade makes money, print `0` (you simply don't trade).

## Input

- Line 1: `n`.
- Line 2: `n` prices.

## Output

One line: the maximum profit, or `0`.

## Example

Input:

```
6
7 1 5 3 6 4
```

Output:

```
5
```

Buy on day 2 (price 1) and sell on day 5 (price 6). Buying at 1 and selling at 7 is not allowed: the 7 comes
**before** the 1.

## Constraints

- `1 <= n <= 200000`
- `1 <= prices[i] <= 10^9`

Use `input()` without a prompt message.
