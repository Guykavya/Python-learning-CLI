## Hint 1

Work out how many units fall into each slab. For 250: 100, 100, 50 and 0. How would you get
each of those numbers from 250?

## Hint 2

Units in the first slab: `min(units, 100)`. Units left after that: `units - 100`, but never
less than 0. `max(0, units - 100)` handles that.

## Hint 3

A clear plan without `min`/`max`: an `if`/`elif` chain on which slab the **last** unit is in,
adding the full cost of all lower slabs: `elif units <= 200: energy = 300 + (units - 100) * 4.5`.
