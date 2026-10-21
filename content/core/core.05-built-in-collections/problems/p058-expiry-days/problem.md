# Remove expired items day by day

A fridge holds items with a number of days until each expires. Read `n`, then `n` lines of
`item days` (days is at least 1), then a number of days `D` to simulate.

On each day from 1 to `D`:

1. every remaining item's days go down by 1;
2. every item that reaches 0 is removed. Print `Day <d>: expired <items>` with the removed items
   in their original order, joined by `, `. If nothing expired, print `Day <d>: nothing expired`.

After the last day, print `Left: <remaining items in original order, joined by ', '>` or
`Left: nothing`.

**Example**

Input:
```
3
milk 2
bread 1
cheese 5
3
```
Output:
```
Day 1: expired bread
Day 2: expired milk
Day 3: nothing expired
Left: cheese
```

Deleting keys from a dict while a `for` loop runs over it raises
`RuntimeError: dictionary changed size during iteration`. Your program must not crash.
