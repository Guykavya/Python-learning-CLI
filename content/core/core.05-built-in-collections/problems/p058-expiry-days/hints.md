## Hint 1

Changing the **values** of a dict while looping over it is fine. Adding or removing keys is not.

## Hint 2

Collect the expired items in a list first, then delete them in a second loop over that list.

## Hint 3

Or rebuild the dict: `fridge = {k: v for k, v in fridge.items() if v > 0}`.
