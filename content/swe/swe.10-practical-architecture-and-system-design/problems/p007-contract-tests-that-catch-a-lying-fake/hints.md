## Hint 1

Do not start from the code; start from the **lies**. For each of the three lying fakes, write down in one sentence what an honest repository does that the liar does not. Then write the smallest scenario (a few calls) after which an honest repository and the liar give **different answers**, and assert the honest answer.

## Hint 2

```text
duplicating:   add the same person twice, then look at members(): honest = one entry
case-sensitive: add "Ana", then ask is_member(project, "ana") and members(): honest = True and ["ana"]
project-blind: add someone to project 1, then ask is_member(2, ...) and members(2): honest = False and []
```

Each check needs its own assert **message** that names the rule, so that a failing check teaches. And keep every check to the interface: a check that peeks at `repo.rows` passes on one implementation only.
