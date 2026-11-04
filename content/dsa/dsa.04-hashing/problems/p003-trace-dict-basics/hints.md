## Hint 1

`ages["ana"] = 31` is an update, not an insert: the key `ana` exists, so only its value changes, and its position in the order stays first.

## Hint 2

`.get(key)` returns `None` for a missing key and prints as `None`. With a second argument it returns that default.

## Hint 3

After `del ages["ben"]` and adding `dev`, the order is ana, dev. `pop` returns the value and removes the key.
