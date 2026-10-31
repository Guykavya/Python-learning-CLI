- Writing `red red red` after `g.color = "red"`. Assigning through an instance never changes the
  class attribute.
- Writing `grey` after `del g.color`. The class was changed to `blue` in the meantime.
- Thinking `g.tags.append(...)` gives `g` its own list. Only assignment creates an instance
  attribute; `append` changes the shared class list, so `Gadget.tags` shows `['new']` too.
- Writing `price is 5`. The property beats the instance dict, even for a key put there by hand.
- Putting `getter runs` **after** `price is 100`. The arguments are evaluated before `print` writes
  anything.
- Writing `pen:blue` for `g.label()` while `g` has its own `label`. Methods lose to the instance dict.
- Missing the second `getter runs`. `hasattr` calls the getter.
