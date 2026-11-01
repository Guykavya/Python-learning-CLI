## Approach

Use the table to find *where* behavior differs, and the documented rules to find *why*. The
four changes:

1. **Boundary**: `weight_kg < limit` should be `<=`. A 1 kg parcel belongs to the "up to 1 kg" band.
2. **Rounding**: `int(total * 100) / 100` truncates (11.5875 becomes 11.58). The original rounds: `round(total, 2)`.
3. **Mutated input**: `extras.append("insured")` writes into the caller's list. Build a new set instead.
4. **Shared default**: `extras=[]` is one list shared by every call. The `append` for a heavy parcel stays in it, so later light parcels get insured too. Use `extras=None`.

Fixing 3 and 4 is one change: copy into a local `names = set(extras or ())`. The tables and
the short function stay.

## Code

```python
def shipping_cost(weight_kg, zone, express=False, extras=None):
    if zone not in RATES:
        raise ValueError(f"unknown zone: {zone}")
    names = set(extras or ())
    cost = RATES[zone]
    for limit, fee in WEIGHT_FEES:
        if weight_kg <= limit:
            cost += fee
            break
    else:
        cost += HEAVY_FEE
    if express:
        cost *= EXPRESS_FACTOR
    total = cost
    if weight_kg > 20:
        names.add("insured")
    if "insured" in names:
        total += cost * INSURED_RATE
    for name in names:
        total += FLAT_EXTRAS.get(name, 0.0)
    return round(total, 2)
```

(The tables at the top of the file are unchanged.)

## Complexity

O(bands + extras), effectively constant.

## Another way

Make the weight lookup a helper: `next((fee for limit, fee in WEIGHT_FEES if weight_kg <= limit), HEAVY_FEE)`.
Money is better kept in integer cents (no rounding surprises at all) or `Decimal`; here the
goal was to match the original exactly. The real lesson: **write the characterization table
before refactoring**. It would have caught all four changes the first time it ran.
