## Hint 1

Which rules are "special cases" that you can deal with first, before any vehicle maths?

## Hint 2

Handle the unknown type and the 0-hour case at the top. Then compute the weekday fee per
vehicle with an `if`/`elif`/`else` chain. Then apply the weekend rule in one place afterwards.

## Hint 3

For a car: `40 if hours <= 2 else 40 + 25 * (hours - 2)`. For a bike: `min(10 * hours, 50)`.
At the weekend: bikes become 0, others get `+ 20`.
