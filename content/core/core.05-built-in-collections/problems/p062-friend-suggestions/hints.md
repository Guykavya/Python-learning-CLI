## Hint 1

Store the network as a dict from each person to a **set** of friends. Add both directions.

## Hint 2

For a person P, loop over each friend F, then over each friend G of F. Count G in a dict
unless G is P or G is already in P's friend set.

## Hint 3

Sort `(-count, name)` tuples and take the first three. Use `friends.get(name, set())` for
unknown names.
