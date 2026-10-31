## Hint 1

Draw boxes and arrows. `team`, `alias` point to one dict. `shallow` is a second dict whose three
values point to the **same** `"A"`, the same members list and the same meta dict as `team`.
`deep` is a third dict whose members list and meta dict are new copies.

## Hint 2

`shallow["name"] = "B"` rebinds a key in the shallow dict only. But `shallow["members"].append(...)`
changes the shared list, and `alias["meta"]["level"] = 2` changes the meta dict that `team`,
`alias` and `shallow` all share. Which dict did `deep["meta"]["level"] = 9` change?

## Hint 3

`r2[0] = [9, 9]` replaces a slot in the new outer list; `r2[1][0] = 8` changes an inner list
that is still shared. `[[0] * 2] * 2` repeats the **same** inner list twice. For tuples:
copying an immutable object returns the object itself; a deep copy of a tuple that contains a
list must make a new list, and so a new tuple.
