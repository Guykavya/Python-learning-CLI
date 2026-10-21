## Approach

The bill depends on which slab the last unit falls in. Lower slabs are always full, so their
cost is a constant.

## Code

```python
units = int(input())
if units < 0:
    print("invalid")
else:
    if units <= 100:
        energy = units * 3.00
    elif units <= 200:
        energy = 300 + (units - 100) * 4.50
    elif units <= 500:
        energy = 300 + 450 + (units - 200) * 6.00
    else:
        energy = 300 + 450 + 1800 + (units - 500) * 8.00
    fixed = 50 if units <= 200 else 100
    print(f"Energy: {energy:.2f}")
    print(f"Fixed: {fixed:.2f}")
    print(f"Total: {energy + fixed:.2f}")
```

## Why constants for full slabs

100 units at 3.00 is 300; 100 at 4.50 is 450; 300 at 6.00 is 1800. Writing the chain this way
keeps each branch simple. Check the boundary values 100, 200 and 500: each should give the
same result from the branch below and the branch above.

## Another way

Count the units in each slab with `min` and `max`, then add them all:

```python
slab1 = min(units, 100)
slab2 = min(max(units - 100, 0), 100)
slab3 = min(max(units - 200, 0), 300)
slab4 = max(units - 500, 0)
energy = slab1 * 3 + slab2 * 4.5 + slab3 * 6 + slab4 * 8
```
