def apply_todo(commits, todo):
    return [subject for _, subject in commits]


def autosquash(commits):
    return [("pick", sha) for sha, _ in commits]
