## Hint 1

Write the starting counts first: 2 categories, 2 suppliers, 3 items, 6 movements, 0 items without a supplier. Then, for each step, look at the model of the thing being deleted and ask: which other models have a `ForeignKey` pointing at it, and what is their `on_delete`?

## Hint 2

Deleting an **item** deletes its movements (`CASCADE`), but nothing points at an item from anywhere else. Deleting a **category** while an item still points at it is refused (`PROTECT`): nothing at all changes. Deleting a **supplier** does not delete items; their `supplier` becomes `NULL` (`SET_NULL`), so `no_supplier` grows by the number of items that pointed to it *at that moment*. A delete that was refused changes no number.

## Hint 3

```text
start        categories=2 suppliers=2 items=3 movements=6 no_supplier=0
1 Hub        Hub's 1 movement goes with it            -> items=2 movements=5
2 Cables     Cable still points at it: PROTECT        -> nothing changes
3 supplier A Cable and Drill get supplier=NULL        -> suppliers=1 no_supplier=2
4 Cable      its 2 movements go with it               -> items=1 movements=3 no_supplier=1
5 Cables     no item points at it any more            -> categories=1
```
