import re


def _regex(pat):
    out = ""
    i = 0
    while i < len(pat):
        if pat.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pat.startswith("/**", i) and i + 3 == len(pat):
            out += "/.*"
            i += 3
        elif pat.startswith("**", i):
            out += ".*"
            i += 2
        elif pat[i] == "*":
            out += "[^/]*"
            i += 1
        elif pat[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pat[i])
            i += 1
    return re.compile("^" + out + "$")


def _rules(patterns):
    rules = []
    for raw in patterns:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        negated = line.startswith("!")
        if negated:
            line = line[1:]
        dir_only = line.endswith("/")
        line = line.rstrip("/")
        anchored = "/" in line
        line = line.lstrip("/")
        rules.append((_regex(line), negated, dir_only, anchored))
    return rules


def _verdict(rules, path, is_dir):
    ignored = False
    for rx, negated, dir_only, anchored in rules:
        if dir_only and not is_dir:
            continue
        target = path if anchored else path.rsplit("/", 1)[-1]
        if rx.match(target):
            ignored = not negated
    return ignored


def is_ignored(path, patterns):
    rules = _rules(patterns)
    is_dir = path.endswith("/")
    path = path.rstrip("/")
    parts = path.split("/")
    for k in range(1, len(parts)):
        if _verdict(rules, "/".join(parts[:k]), True):
            return True
    return _verdict(rules, path, is_dir)
