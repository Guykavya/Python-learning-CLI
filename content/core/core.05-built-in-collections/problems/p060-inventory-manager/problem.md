# Inventory manager

Build an inventory manager. Each item has a quantity and a price per unit (whole rupees). Read
commands until `end`:

| Command | Behaviour |
|---|---|
| `stock ITEM QTY PRICE` | add QTY to ITEM (new items start at 0) and set its price to PRICE. Print `Stocked ITEM: QTY_NOW` |
| `sell ITEM QTY` | unknown item: `Unknown item ITEM`. Not enough: `Not enough ITEM (have K)`. Otherwise reduce the quantity, add `QTY × price` to revenue, print `Sold QTY ITEM for AMOUNT` |
| `low N` | items with quantity **below** N, sorted by quantity then name, as `ITEM QTY`; or `No low stock` |
| `report` | every item sorted by stock value (`qty × price`), **highest first**, ties by name: `ITEM QTY x PRICE = VALUE`; then `Total value: T` |

Items stay in the inventory even when their quantity reaches 0. After `end`, print
`Revenue: R`.

**Example**

Input:
```
stock pen 10 5
stock ink 4 30
stock pad 20 5
sell pen 3
sell ink 5
sell glue 1
stock pen 2 6
low 10
report
end
```
Output:
```
Stocked pen: 10
Stocked ink: 4
Stocked pad: 20
Sold 3 pen for 15
Not enough ink (have 4)
Unknown item glue
Stocked pen: 9
ink 4
pen 9
ink 4 x 30 = 120
pad 20 x 5 = 100
pen 9 x 6 = 54
Total value: 274
Revenue: 15
```

The second `stock pen` adds 2 pens and changes the price to 6. `low 10` lists `ink` and `pen`.
