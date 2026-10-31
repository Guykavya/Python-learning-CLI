## Approach

Each decision in the function gets both outcomes, and every call carries an exact expected value:

- `weight <= 0`: `pytest.raises(ValueError)` (true) and any later call (false).
- `weight > 20` / `elif weight > 5`: calls at 25, 10 and 3 kg take the three paths; the borders 5, 20 and 21 catch the `>` versus `>=` bugs that coverage cannot see.
- `zone == "abroad"` with and without `express` (the `ValueError`), and the `elif express:` at home.
- the loop: `[]` skips it, `["NOPE"]` runs it to the end without returning, `["FREE"]` returns inside it, `["HALF"]` takes the `break`.

Coverage tells you which of these you forgot; the exact `==` values (and the borders) are what kill the buggy versions. A suite with 100% branch coverage and no
asserts would pass every mutant.

## Code

```python
import pytest

from target import parcel_fee


def test_weight_must_be_positive():
    with pytest.raises(ValueError):
        parcel_fee(0, "home", False, [])
    with pytest.raises(ValueError):
        parcel_fee(-3, "home", False, [])


def test_weight_classes():
    assert parcel_fee(3, "home", False, []) == 500, "Up to 5 kg: only the base fee."
    assert parcel_fee(10, "home", False, []) == 1000, "Over 5 kg: base + 500."
    assert parcel_fee(25, "home", False, []) == 2000, "Over 20 kg: base + 1500."


def test_weight_borders():
    assert parcel_fee(5, "home", False, []) == 500, "Exactly 5 kg is still light."
    assert parcel_fee(20, "home", False, []) == 1000, "Exactly 20 kg is not 'over 20'."
    assert parcel_fee(21, "home", False, []) == 2000, "21 kg is heavy."


def test_zones_and_express():
    assert parcel_fee(3, "abroad", False, []) == 1500, "Abroad triples the fee."
    assert parcel_fee(10, "abroad", False, []) == 3000, "The weight surcharge is tripled too."
    assert parcel_fee(3, "home", True, []) == 1500, "Express at home adds 1000."
    with pytest.raises(ValueError):
        parcel_fee(3, "abroad", True, [])


def test_coupons():
    assert parcel_fee(10, "home", False, ["FREE"]) == 0, "FREE makes the parcel free."
    assert parcel_fee(10, "home", False, ["HALF"]) == 500, "HALF halves 1000."
    assert parcel_fee(3, "home", True, ["HALF"]) == 750, "HALF halves 1500."
    assert parcel_fee(3, "home", False, ["HALF", "FREE"]) == 250, "Codes after HALF are ignored."
    assert parcel_fee(3, "home", False, ["NOPE"]) == 500, "An unknown code does nothing."
    assert parcel_fee(3, "home", False, ["NOPE", "HALF"]) == 250, "A later HALF still works."
    assert parcel_fee(3, "home", False, ["NOPE", "FREE"]) == 0, "A later FREE still works."
```

## Cost

Five tests and about twenty calls: instant. Measuring branches slows the traced code down a few times, which does not matter at this size.

## Another way

`@pytest.mark.parametrize("weight, zone, express, coupons, fee", [...])` with one row per call shows the whole table at a glance and reports each row separately. Keep the
`pytest.raises` cases as separate tests.
