## Hint 1

What does the lot need to remember? Which plate is in which spot, and which spot each plate is in.
Two dicts make both questions fast: `spot -> plate or None`, and `plate -> spot`. If you fill the
first dict in the order `S1, S2, ..., L1, L2, ...`, how does a simple loop find the free spot with
the lowest number?

## Hint 2

Clean the plate first in every method: `plate = plate.strip().upper()`. Then check in this order:
bad size, already parked, find a spot, no spot. Change the dicts only after all checks pass.
For a small car: "first free small spot, or else first free large spot" can be written with `or`,
because a missing spot is `None`.

## Hint 3

```
__init__: self._spots = {"S1": None, ..., "L1": None, ...};  self._where = {}

_first_free(prefix):
    for name, plate in self._spots.items():
        if name starts with prefix and plate is None: return name
    return None

park(plate, size):
    check size; plate = clean(plate)
    if plate in self._where: raise AlreadyParkedError(plate, self._where[plate])
    spot = first_free("L") if size == "large" else (first_free("S") or first_free("L"))
    if spot is None: raise LotFullError(size)
    self._spots[spot] = plate; self._where[plate] = spot
    return spot
```
