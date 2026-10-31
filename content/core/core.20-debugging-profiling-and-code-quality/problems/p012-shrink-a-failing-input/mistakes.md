- Stopping after the first pass. A pass that removed something may have made other removals
  possible; only a pass that removed **nothing** proves 1-minimal.
- Moving to `i + 1` after a successful removal. The next element has slid into position `i`
  and is skipped.
- `current.remove(x)` by value. With duplicates it removes the first equal element, not the one
  at position `i`.
- Changing `current` in place and passing it to `fails`: if the removal turns out not to fail,
  you must undo it, and it is easy to forget.
- Trying every subset with `itertools.combinations`. It is correct and finishes for 6 items, but
  needs 2^300 calls for 300.
- Returning the original `items` list object (or shrinking it in place). The caller's data must
  not change.
