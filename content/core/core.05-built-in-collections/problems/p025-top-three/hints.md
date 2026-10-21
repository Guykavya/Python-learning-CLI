## Hint 1

Tuples sort by their first item, then by the second to break ties. What tuple would put high
scores first and break ties alphabetically?

## Hint 2

`(-score, name)`: the negative makes larger scores sort earlier; the name breaks ties A to Z.

## Hint 3

Build `ranked = sorted((-score, name) for ...)`, take `ranked[:3]`, and print `-neg` to get the
score back.
