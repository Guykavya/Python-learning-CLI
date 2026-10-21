**1. Alias.** `alias = team` copies nothing. It attaches a second name to the same outer list.
Any change to that list, or to anything inside it, is visible through both names. So `alias`
shows the new mark and Meena.

**2. Shallow copy.** `team.copy()` makes a **new outer list**, but fills it with the **same
references** as the old one. The two outer lists point to the same inner lists
`['Asha', ...]` and `['Ravi', ...]`. Changing `team[0][1]` changes the shared inner list,
so `shallow` sees 90. Appending Meena changes only `team`'s outer list; `shallow`'s outer list
has no slot for her.

**3. Deep copy.** `copy.deepcopy(team)` makes a new outer list **and** new copies of every
mutable thing inside, recursively. `deep` shares no list with `team`, so neither change shows.
(The strings and ints inside are not copied, but they are immutable, so sharing them is safe.)

**4. Memory after the copies:**

```
team, alias --> [ o , o ]            outer list A
                  |   |
                  v   v
          ['Asha',82] ['Ravi',75]    inner lists (shared)
                  ^   ^
                  |   |
shallow ------> [ o , o ]            outer list B

deep ---------> [ o , o ]            outer list C
                  |   |
                  v   v
          ['Asha',82] ['Ravi',75]    its own inner lists
```

**5. Other ways.** Shallow: `list(team)`, `team[:]`, `copy.copy(team)`. Deep for a list of lists
of immutable values: `[row[:] for row in team]` (or `[row.copy() for row in team]`). That works
one level down; for deeper nesting use `copy.deepcopy`.

Key ideas to check: assignment makes an alias; a shallow copy has a new outer list but shared
inner objects; replacing versus mutating; deepcopy copies all mutable levels; a correct diagram.
