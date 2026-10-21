## Hint 1

After sorting, where in the list does a player with a given score first appear?

## Hint 2

Walk the sorted list with `enumerate(start=1)`. The rank of a player equals the position of
the **first** player with the same score.

## Hint 3

Keep `rank_of = {}`. For position `i` and score `s`: `if s not in rank_of: rank_of[s] = i`.
