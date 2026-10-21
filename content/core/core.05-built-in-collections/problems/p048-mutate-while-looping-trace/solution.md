## Walkthrough

**Loop 1** on `[1, 2, 3, 4, 5, 6]`: position 1 is `2`, removed; the list becomes
`[1, 3, 4, 5, 6]` and position 2 is now `4`, removed; then position 3 is `6`, removed. The
result `[1, 3, 5]` **looks right by luck**: the odd numbers that were skipped did not need
removing.

**Loop 2** on `[2, 2, 4, 5]`: position 0 is `2`, removed, giving `[2, 4, 5]`; position 1 is `4`,
removed, giving `[2, 5]`; position 2 does not exist, so the loop ends. A `2` survives: `[2, 5]`.

**Loop 3** appends `10` while looping, so the loop also visits `10`: `[1, 2, 3, 10]`.

**Loop 4** assigns through the index, so the list changes: `[10, 12, 14]`.

**Loop 5** only rebinds `v`, so `vals` is unchanged: `[10, 12, 14]`.

The comprehension builds a new list of the odd numbers: `[5]`.
