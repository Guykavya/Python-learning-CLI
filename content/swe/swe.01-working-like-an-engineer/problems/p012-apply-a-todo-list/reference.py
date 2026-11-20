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
