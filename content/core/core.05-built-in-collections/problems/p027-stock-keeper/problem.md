# Stock keeper

Keep track of a shop's stock. Read commands until `end`:

| Command | What to do |
|---|---|
| `add ITEM N` | increase ITEM's quantity by N |
| `sell ITEM N` | decrease by N; if there is not enough, print `Cannot sell N ITEM: only K left` and change nothing |
| `check ITEM` | print `ITEM: K` (0 for an item never added) |

After `end`, print `Stock:` and then each item with a quantity above zero, sorted by item name,
as `ITEM K`. If nothing is in stock, print `(nothing in stock)` after `Stock:`.

**Example**

Input:
```
add pen 10
add ink 3
sell pen 4
sell ink 5
check ink
check glue
sell ink 3
add pad 2
end
```
Output:
```
Cannot sell 5 ink: only 3 left
ink: 3
glue: 0
Stock:
pad 2
pen 6
```
