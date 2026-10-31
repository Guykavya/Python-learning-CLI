# Reach every branch

Line coverage says "this line ran". **Branch coverage** says "this `if` was true at least once **and** false at least once; this loop
ran, and was also skipped". Here is a function with many branches:

```python
def parcel_fee(weight, zone, express, coupons):
    """Fee in cents for a parcel.

    Base 500. Over 20 kg add 1500; over 5 kg (up to 20) add 500. Zone "abroad" multiplies by 3
    and does not allow express (ValueError); at home, express adds 1000. A weight of 0 or less is a
    ValueError. Then the coupon codes are read in order: "FREE" makes the parcel free at once,
    "HALF" halves the fee (rounded down) and ignores the codes after it. Other codes do nothing.
    """
    if weight <= 0:
        raise ValueError("weight must be positive")
    fee = 500
    if weight > 20:
        fee += 1500
    elif weight > 5:
        fee += 500
    if zone == "abroad":
        fee *= 3
        if express:
            raise ValueError("no express abroad")
    elif express:
        fee += 1000
    for code in coupons:
        if code == "FREE":
            return 0
        if code == "HALF":
            fee //= 2
            break
    return fee
```

In `solution.py` write tests (`from target import parcel_fee`; save the function as `target.py` in your folder). The checker runs your tests under
`coverage` with branch measurement turned on and demands **all three**:

1. your tests **pass** on the correct function (at least 5 test functions);
2. **every line and every branch** of `parcel_fee` was run (the report names any line or jump you missed);
3. your tests **fail** on each of eight buggy versions, so they must really `assert` the exact fee and not only call the function.

To see your own coverage while you work:

```bash
python -m coverage run --branch -m pytest solution.py
python -m coverage report -m
```

Hint about borders: coverage is satisfied by `weight = 25`, but only an exact test at 20 and 21 kg catches a `>` written as `>=`. Reaching a branch is
not the same as checking it.

**Example**

```python
def test_light_parcel_pays_the_base_fee():
    assert parcel_fee(3, "home", False, []) == 500, "Up to 5 kg only the base fee is charged."
```

**How this is checked.** Your `solution.py` is copied next to the function (saved as `target.py`) and run by real pytest inside a coverage
measurement; first on the correct function (everything must pass and be covered), then on each buggy copy
(at least one of your tests must fail on each).
