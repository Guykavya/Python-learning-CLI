## Model answer

1. **Why the memory stays.** `data[:10]` is a basic slice, so it is a **view**: a new array header (shape, strides, a pointer) that reads the same memory block as `data`. It has no data of its own. To keep those ten numbers valid, the view keeps a **reference** to the array that owns the block, its **base**. Python frees memory only when nothing refers to it any more, and the returned view still does. So the whole 1 GB block of each file stays alive as long as the ten-number view lives: three files, three gigabytes. The local name `data` disappearing does not matter; the **reference keeps the memory** alive.

2. **How to check.** `part.base is not None` (or `part.base.nbytes`, which here shows 1,000,000,000 bytes behind an 80-byte array), `part.flags["OWNDATA"]` is `False`, and `np.shares_memory(part, data)` is `True` while you still have `data`.

3. **The fix: `.copy()`.** `return data[:10].copy()`. A copy allocates its own 80 bytes and has `base is None`, so nothing refers to the big block once the function returns and Python can free it. In short: **copy the small part** you keep.

4. **When a view is right.** When you still need the big array anyway, or the piece is large, or you want writes to reach the original (for example editing a region of an image in place). Then the view saves memory and time, which is why NumPy makes views by default.

**Checklist: your answer should mention**
- [ ] a basic slice is a view, not a copy
- [ ] the view keeps a reference to its base array
- [ ] memory is freed only when no reference remains, so the whole base stays alive
- [ ] how to check: `.base`, `OWNDATA` or `np.shares_memory`
- [ ] the fix: copy the small part (`.copy()`), whose base is `None`
- [ ] when a view is the better choice
