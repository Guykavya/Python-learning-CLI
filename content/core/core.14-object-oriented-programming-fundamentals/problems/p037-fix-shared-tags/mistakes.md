- Fixing only `tags=None` but keeping `self.tags = tags` when a list is given. The note still shares
  (and changes) the caller's list.
- `self.tags = list(tags)` and then `self.tags[:] = cleaned`. That works, but fixing the cleaning
  while copying is simpler: append clean tags to a new list.
- Keeping `history = []` in the class body "as a default" and also adding `self.history = []` in
  `__init__`. It works, but the class-level list is a trap for the next reader; remove it.
- "Fixing" `count` too, by moving it into `__init__` as `self.count`. A per-note counter is always 1.
- Thinking `self.history.append(x)` creates an instance attribute. Only **assignment**
  (`self.history = ...`) creates one; `append` changes whatever list lookup finds.
- Copying the tags in `add_tag` instead of in `__init__`. The sharing starts in `__init__`.
