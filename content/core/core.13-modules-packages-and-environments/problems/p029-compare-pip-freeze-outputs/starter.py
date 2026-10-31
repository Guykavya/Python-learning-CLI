def normalise(name):
    # TODO: lowercase, runs of - _ . become one -
    return name


def parse_freeze(text):
    # TODO: skip blanks, comments and option lines; read name==version and name @ url
    return {}


def diff_freeze(old_text, new_text):
    # TODO: added, removed, upgraded, downgraded, changed
    return {"added": [], "removed": [], "upgraded": [], "downgraded": [], "changed": []}


def format_diff(diff):
    # TODO: one line per difference, or ["no changes"]
    return []
