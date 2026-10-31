# A parking lot with its own errors

A parking lot has **small** spots and **large** spots. Write the class `ParkingLot` and its
exceptions in `solution.py`.

**Exceptions**

- `ParkingError(Exception)`: the base of all three below.
- `LotFullError(ParkingError)`: `LotFullError(size)` stores `size`; message `f"no free spot for a {size} car"`.
- `AlreadyParkedError(ParkingError)`: `AlreadyParkedError(plate, spot)` stores `plate` and `spot`;
  message `f"{plate} is already parked at {spot}"`.
- `NotParkedError(ParkingError)`: `NotParkedError(plate)` stores `plate`; message `f"{plate} is not parked here"`.

**`ParkingLot(small, large)`** has `small` small spots named `S1`, `S2`, ... and `large` large
spots named `L1`, `L2`, .... Both numbers must be `int`s of 0 or more, otherwise `ValueError`.

Plates are compared after `strip().upper()`, so `" ka01 "` and `"KA01"` are the same car, and
methods report plates in that form.

- `park(plate, size)`: `size` is `"small"` or `"large"`, otherwise `ValueError`.
  - A car that is already parked raises `AlreadyParkedError`.
  - A **large** car needs a large spot. A **small** car takes a small spot if one is free, and
    otherwise a large spot.
  - Always take the free spot with the **lowest number** of the right kind.
  - If no spot fits, raise `LotFullError(size)`.
  - Return the spot name, like `"S1"`.
- `leave(plate)`: frees the car's spot and returns its name. A car that is not parked raises
  `NotParkedError`.
- `where(plate)`: the spot name of the car, or `None`.
- `free(kind)`: the number of free spots of that kind (`"small"` or `"large"`).
- `report()`: a list of `"<spot> <plate>"` lines for the taken spots only: all small spots first,
  then large, each kind in number order (`S2` before `S10`).

**Example**

```python
lot = ParkingLot(small=2, large=1)
lot.park("ka01", "small")    # 'S1'
lot.park("KA02", "small")    # 'S2'
lot.park("ka03", "small")    # 'L1'   (small spots are full, so a large one)
lot.park("ka04", "large")    # LotFullError: no free spot for a large car
lot.park(" ka02 ", "small")  # AlreadyParkedError: KA02 is already parked at S2
lot.leave("ka01")            # 'S1'
lot.free("small")            # 1
lot.report()                 # ['S2 KA02', 'L1 KA03']
lot.leave("zz99")            # NotParkedError: ZZ99 is not parked here
```
