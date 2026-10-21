## Hint 1

Count with a dict and `get(name, 0) + 1`.

## Hint 2

Sort `(-votes, name)` tuples for the table. The best count is `max(counts.values())`.

## Hint 3

The tied leaders are `sorted(name for name, v in counts.items() if v == best)`.
