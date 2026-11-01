# Fix: the refactor that changed behavior

A teammate "cleaned up" `shipping_cost` into the table-driven version in `starter.py` and
said "no behavior change, just tidier". Customers disagree: some prices are a cent off and
some are wrong. You no longer have the old code, only its **documented behavior** and a table
of prices it produced.

**The original behavior**

```python
def shipping_cost(weight_kg, zone, express=False, extras=None):
    """Price of a parcel in the currency units of the tables.

    - zone must be in RATES, otherwise ValueError("unknown zone: ...").
    - Start with the zone rate, then add the weight fee of the FIRST band whose
      limit is >= weight_kg (limits are inclusive: 1 kg is in the first band).
      Above the last limit add HEAVY_FEE.
    - If express, multiply that subtotal by EXPRESS_FACTOR.
    - extras is None or an iterable of names; duplicates count once, unknown names
      are ignored. Parcels over 20 kg are always insured, even if "insured" was not
      asked for. Insurance costs INSURED_RATE of the subtotal (after express).
      Flat extras (FLAT_EXTRAS) are added after that.
    - The result is ROUNDED to 2 decimals (round(total, 2)).
    - It never changes its arguments and remembers nothing between calls.
    """
```

**The table** (every row is real output of the original)

| weight | zone | express | extras | price |
|---|---|---|---|---|
| 0.5 | local | no | none | 5.0 |
| 1 | local | no | none | 5.0 |
| 1.01 | local | no | none | 7.5 |
| 3 | national | no | none | 10.5 |
| 5 | national | no | none | 10.5 |
| 5.5 | national | no | none | 15.5 |
| 20 | world | no | none | 27.5 |
| 20.5 | world | no | none | 36.05 |
| 3 | national | yes | none | 15.75 |
| 3 | local | no | fragile | 10.5 |
| 3 | local | no | fragile, signature, fragile | 12.0 |
| 3 | national | no | insured | 10.81 |
| 3 | national | yes | insured, fragile | 19.22 |
| 1.5 | local | yes | insured | 11.59 |
| 30 | world | no | none | 36.05 |
| 2 | local | no | gift (unknown) | 7.5 |

Copy `starter.py` to `solution.py` and **fix the refactor so it behaves like the original
again**. Do not "un-clean" it: keep the tables and the short function, and do not rewrite it
as a long `if/elif` ladder (the tests check this).

Four behaviors were changed. Find them by running the table, then by reading the starter for
the things a table cannot show.

**Example** (one of the rows)

```python
shipping_cost(1.5, "local", True, ["insured"])   # the original gives 11.59; the starter gives 11.58
```
