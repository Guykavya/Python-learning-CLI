## Approach

```python
def apply_todo(commits, todo):
    by_sha = dict(commits)
    result = []          # list of [subject]; one entry per resulting commit
    for item in todo:
        cmd, sha = item[0], item[1]
        if cmd not in ("pick", "reword", "squash", "fixup", "drop"):
            raise ValueError(f"unknown command: {cmd}")
        if sha not in by_sha:
            raise ValueError(f"unknown commit: {sha}")
        if cmd == "pick":
            result.append(by_sha[sha])
        elif cmd == "reword":
            result.append(item[2])
        elif cmd in ("squash", "fixup"):
            if not result:
                raise ValueError(f"cannot '{cmd}' without a previous commit")
        # drop: nothing to do; squash/fixup keep the subject of the commit above
    return result


def autosquash(commits):
    groups = []          # each group: list of (command, sha); the first is the target
    index = {}           # subject -> group of the first commit with that subject
    for sha, subject in commits:
        cmd = None
        for prefix in ("fixup! ", "squash! "):
            if subject.startswith(prefix):
                cmd = prefix[:-2]
                target = subject[len(prefix):]
        if cmd and target in index:
            index[target].append((cmd, sha))
            continue
        group = [("pick", sha)]
        groups.append(group)
        index.setdefault(subject, group)
    return [step for group in groups for step in group]
```

`apply_todo` keeps only subjects. A `squash`/`fixup` changes nothing in that list (the target keeps its subject) and only checks that a target exists. `autosquash` builds groups so that moving a fixup "right after its target" is just appending to that target's group; flattening the groups gives git's order.

Example: for the four commits of the statement the groups are `[a1, c3 (fixup)]`, `[b2]`, `[d4]`. Flattened: `pick a1, fixup c3, pick b2, pick d4`.

## Complexity

`O(n)` for both (dictionary lookups).

## Another way

Git matches the text after `fixup! ` also as a **prefix** of a subject or as a commit hash. This model uses exact subjects, which is what `git commit --fixup` writes.

## Why it matters

`git commit --fixup <commit>` plus `git rebase -i --autosquash` (chapter section 7.7) is the cleanest way to correct an older commit of your branch. This is the logic behind it.
