## Hint 1

`name, rest = line.split(":")` separates the name. `set(rest.split())` gives the friends.

## Hint 2

Mutual is an intersection. A suggestion is a difference, minus the person themselves:
`b_friends - a_friends - {a}`.

## Hint 3

The network is the union of both friend sets and both names: `a_friends | b_friends | {a, b}`.
