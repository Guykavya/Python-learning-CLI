## Hint 1

Smallest first: the sticks are `2, 3, 4, 6`. The first round pops 2 and then 3. The new stick 5 goes back; now the sticks are `4, 5, 6`. Which two come out next?

## Hint 2

Largest first: the heap holds `-2, -4, -3, -6`. The smallest entry is `-6`, so `a = 6`; the next is `-4`, so `b = 4`. The new stick `10` is pushed as `-10`, which is now the smallest entry. Keep going: it is always the stick that was just made plus the largest one left.

## Hint 3

The totals are the sums of the three join costs. Smallest first: `5 + 9 + 15`. Largest first: `10 + 13 + 15`. The last join always costs 15 (the sum of all sticks), whatever the order.
