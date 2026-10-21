## Hint 1

A dict from item to quantity. `stock.get(item, 0)` handles items that were never added.

## Hint 2

For `sell`, compare `N` with `stock.get(item, 0)` before changing anything.

## Hint 3

At the end, loop over `sorted(stock)` and skip items whose quantity is 0.
