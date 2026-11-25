## Approach

Counts: view 10, cart 7, checkout 4, buy 2.

- view: 10 / 12 = 83.3 of the previous (all) and of all.
- cart: 7 / 10 = 70.0 of the previous, 7 / 12 = 58.3 of all.
- checkout: 4 / 7 = 57.1, 4 / 12 = 33.3.
- buy: 2 / 4 = 50.0, 2 / 12 = 16.7.

## Code

```text
view      10  83.3  83.3
cart       7  70.0  58.3
checkout   4  57.1  33.3
buy        2  50.0  16.7
```

## Complexity

Not applicable (a trace problem).

## Another way

The largest loss in numbers is view to cart (3 sessions) and the largest loss as a share is checkout to buy (50%): the biggest drop in absolute terms is not always the best place to work.
