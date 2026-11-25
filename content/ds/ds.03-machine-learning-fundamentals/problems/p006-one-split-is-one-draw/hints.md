## Hint 1

For each seed, first write the rotated list: slide `k = 2 * seed` rows from the front to the back. The test set is the last three rows of that list.

## Hint 2

For each test row apply the rule (`x >= 3` gives 1) and compare with the label. The accuracy is hits divided by 3, printed with three decimals.
