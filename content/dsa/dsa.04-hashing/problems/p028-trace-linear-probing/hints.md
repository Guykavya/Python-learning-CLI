## Hint 1

Keys 10, 17, 3, 24 all have home slot 3 (10 % 7 = 3, 17 % 7 = 3, 3 % 7 = 3, 24 % 7 = 3). They fill slots 3, 4, 5, 6.

## Hint 2

8 % 7 = 1 goes to slot 1. 15 % 7 = 1 finds slot 1 taken, so it goes to slot 2.

## Hint 3

Searches follow the probe run until an empty slot (`None`). The table is `[None, 8, 15, 10, 17, 3, 24]`, so a search that wraps past slot 6 meets the empty slot 0.
