## Approach

A model can hold several relationships between the same two tables; only one is active. `USERELATIONSHIP` inside `CALCULATE` activates another one **for that calculation only**.

## Code

```python
def ship_date_measure():
    return "CALCULATE([Revenue], USERELATIONSHIP(Sales[ShipDateKey], Date[DateKey]))"
```

## Complexity

O(1) to write.

## Another way

Make a **second date table** (a copy called `ShipDate`) with its own active relationship: simpler for report authors, at the price of a duplicated table and its slicers.
