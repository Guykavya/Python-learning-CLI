See the model answer shown when you check. The ideas that must appear:


1. `alias` is a second name for the same outer list, so every change is visible.
2. `copy()` makes a new outer list holding the same inner list references. Changing an inner
   list shows; appending to `team`'s outer list does not.
3. `deepcopy` copies the outer list and every inner list, so nothing is shared.
4. The diagram: one outer list for `team`/`alias`, one for `shallow` pointing at the same rows,
   one for `deep` pointing at its own rows.
5. `list(team)`, `team[:]` and `copy.copy(team)`; `[row[:] for row in team]`.
