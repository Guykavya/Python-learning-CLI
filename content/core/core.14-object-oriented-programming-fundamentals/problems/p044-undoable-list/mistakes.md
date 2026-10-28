- `class UndoableList(list)`. Then `u.sort()` or `u[0] = "x"` change the list with no undo record.
- Recording the index as given (`-1`, `-3`). After the change, the same negative number points to a
  different place, so undo puts the item back in the wrong spot.
- Recording before checking the index. A failed `pop(5)` then leaves a fake record, and the next
  `undo` reverses a change that never happened.
- Forgetting to clear the redo stack on a new change. Redo then applies an old change on top of a
  list it no longer fits.
- For `clear`, recording `self._items` itself instead of a copy. After `clear()` that list is empty,
  so undo restores nothing.
- `undo` that only reverses but does not push the record onto the redo stack, so `redo` has nothing.
