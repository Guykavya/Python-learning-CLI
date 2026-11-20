## Approach

Start from `categories=2 suppliers=2 items=3 movements=6 no_supplier=0` and apply the five deletes in order.

```text
1: deleted categories=2 suppliers=2 items=2 movements=5 no_supplier=0
2: ProtectedError categories=2 suppliers=2 items=2 movements=5 no_supplier=0
3: deleted categories=2 suppliers=1 items=2 movements=5 no_supplier=2
4: deleted categories=2 suppliers=1 items=1 movements=3 no_supplier=1
5: deleted categories=1 suppliers=1 items=1 movements=3 no_supplier=1
```

- **1.** `hub.delete()`: `Movement.item` is `CASCADE`, so Hub's one movement is deleted with it (movements 6 to 5). Nothing else changes; supplier B keeps living.
- **2.** `cables.delete()`: `Item.category` is `PROTECT` and Cable still points at Cables. Django checks this **before** deleting anything and raises `ProtectedError`: all counts stay as they were.
- **3.** `supplier_a.delete()`: `Item.supplier` is `SET_NULL`. Cable and Drill both pointed at A, so both get `supplier = NULL` (`no_supplier=2`). Items and movements are untouched.
- **4.** `cable.delete()`: its 2 movements are cascaded (movements 5 to 3). Items: 2 to 1. Cable was one of the two items without a supplier, so `no_supplier` goes to 1 (Drill).
- **5.** `cables.delete()` now works: no item points at Cables any more (Cable and Hub are both gone). Categories: 2 to 1. Drill still belongs to Tools.

Real output of the program, run with Django 6.1.3.

Rule of thumb: `CASCADE` for parts that have no meaning without their parent (movements of an item), `PROTECT` for things that carry history or that you must never lose by accident (a category with items, a product that was sold), `SET_NULL` for optional links (a preferred supplier).

## Complexity

Not applicable; this is a reading exercise. (In the database a `CASCADE` delete walks the related rows, so deleting a parent with a million children is a million deletes.)

## Another way

`on_delete=models.RESTRICT` is like `PROTECT` but allows the delete when the blocking row would itself be deleted by a cascade in the same operation. `SET_DEFAULT` and `DO_NOTHING` exist too; `DO_NOTHING` leaves the integrity check to the database and usually ends in an `IntegrityError`.
