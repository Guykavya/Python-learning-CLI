## Hint 1

Make a small table by hand for amounts 7 to 12: what does the machine pay (as many 4s as fit, then 3s, then 1s), and what is the best you can do? Look for remainders: after greedy's 4s, a remainder of 2 can only be paid as `1 + 1`.

## Hint 2

Amounts that leave remainder 2 after the 4s: 6, 10, 14, ... For 10 the machine pays `4 + 4 + 1 + 1`. Can you pay 10 with three coins using a 3? Check that no answer uses only two coins (the biggest two coins make only 8).

## Hint 3

```
amount  = an amount like 10
machine = greedy_coins(amount)          # trace it by hand
better  = a list of 1/3/4 coins adding to amount, with fewer coins
return (amount, machine, better)
```
Check "fewest" by asking: could one coin fewer ever reach `amount`? With `k` coins the most you can pay is `4 * k`.
