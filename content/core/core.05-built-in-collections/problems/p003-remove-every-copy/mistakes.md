- Calling `words.remove(target)` once. It removes only the first copy.
- Looping `for w in words:` and removing inside the loop. Adjacent copies get skipped
  (try `a a a` with target `a`).
- Calling `remove` when the word is not in the list at all, which raises `ValueError`.
