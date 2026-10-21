# Electricity bill slabs

Read the units of electricity used (a whole number). The energy charge uses **slabs**:
each unit is charged at the rate of the slab it falls in.

| Units | Rate per unit |
|---|---|
| 1 to 100 | 3.00 |
| 101 to 200 | 4.50 |
| 201 to 500 | 6.00 |
| above 500 | 8.00 |

So 250 units cost `100 * 3.00 + 100 * 4.50 + 50 * 6.00 = 1050.00`.

There is also a fixed charge: **50** if the units are 200 or less, otherwise **100**.

Print three lines, with 2 decimals:

```
Energy: <energy charge>
Fixed: <fixed charge>
Total: <energy + fixed>
```

If the units are negative, print only `invalid`.

**Example**

Input `250`. Output:

```
Energy: 1050.00
Fixed: 100.00
Total: 1150.00
```
