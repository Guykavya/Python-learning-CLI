## Hint 1

Group marks by name: a dict from name to a list of marks, filled with `setdefault`.

## Hint 2

For each name, `avg = sum(ms) / len(ms)`. Build tuples `(-avg, name, count)`.

## Hint 3

Sort the tuples. The negative average puts high averages first; the name breaks ties.
