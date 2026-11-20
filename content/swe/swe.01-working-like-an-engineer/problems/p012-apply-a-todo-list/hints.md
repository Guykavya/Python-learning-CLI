## Hint 1

For `apply_todo`: a result list of subjects. What happens to it for each command? Which commands add an entry, and which do not?

## Hint 2

`squash` and `fixup` add **no** entry; they only require that the list is not empty. For `autosquash`, think of **groups**: every `pick` starts a group `[("pick", sha)]`; a fixup is appended to the group of its target.

## Hint 3

```text
autosquash:
    groups = []; first_group_of_subject = {}
    for sha, subject in commits:
        if subject starts with "fixup! " or "squash! " and the rest is in first_group_of_subject:
            first_group_of_subject[rest].append((cmd, sha))
        else:
            g = [("pick", sha)]; groups.append(g); first_group_of_subject.setdefault(subject, g)
    return all steps of all groups, group by group
```
