## Hint 1

First call: the list is empty, so `prev.next` is `None` and the loop does not run. `prev` is still the dummy, whose value is `"D"`. What is the list after linking 4?

## Hint 2

For inserting the second `4` into `2 -> 4 -> 6`: is `2 < 4`? Then `prev` moves to `2`. Is `4 < 4`? No, so `prev` stops on `2`, and the new `4` goes between `2` and the old `4`.
