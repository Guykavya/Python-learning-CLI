## Hint 1

An index helps when it lets the database **skip** most of the table. What fraction of the table does `is_active = 1` skip?

## Hint 2

Using an index means: look up an entry, then jump to the table row, for every match. Reading the table in order is one sweep. Which is cheaper for 900,000 matches?

## Hint 3

The planner estimates how many rows match, using statistics. For a "latest 50 active users" page, think of a composite index that also provides the ordering, with `LIMIT`.
