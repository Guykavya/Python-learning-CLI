SEPARATORS = "-_."


def normalise(name):
    out = []
    for ch in name.strip().lower():
        if ch in SEPARATORS:
            if not out or out[-1] != "-":
                out.append("-")
        else:
            out.append(ch)
    return "".join(out)


def parse_freeze(text):
    packages = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        if "==" in line:
            name, _, version = line.partition("==")
            version = version.strip()
        elif " @ " in line:
            name, _, url = line.partition(" @ ")
            version = "@ " + url.strip()
        else:
            raise ValueError(f"line {number}: cannot read {line!r}")
        name = normalise(name)
        if not name or not version or version == "@ ":
            raise ValueError(f"line {number}: cannot read {line!r}")
        if name in packages:
            raise ValueError(f"line {number}: {name} appears twice")
        packages[name] = version
    return packages


def _as_numbers(version):
    """(1, 26, 18) for '1.26.18' with trailing zeros removed, or None if not only numbers."""
    parts = version.split(".")
    if not all(p.isdigit() for p in parts):
        return None
    numbers = [int(p) for p in parts]
    while len(numbers) > 1 and numbers[-1] == 0:
        numbers.pop()
    return tuple(numbers)


def diff_freeze(old_text, new_text):
    old = parse_freeze(old_text)
    new = parse_freeze(new_text)
    diff = {"added": [], "removed": [], "upgraded": [], "downgraded": [], "changed": []}
    for name in sorted(old.keys() | new.keys()):
        if name not in old:
            diff["added"].append((name, new[name]))
        elif name not in new:
            diff["removed"].append((name, old[name]))
        elif old[name] != new[name]:
            a, b = _as_numbers(old[name]), _as_numbers(new[name])
            if a is None or b is None:
                diff["changed"].append((name, old[name], new[name]))
            elif b > a:
                diff["upgraded"].append((name, old[name], new[name]))
            elif b < a:
                diff["downgraded"].append((name, old[name], new[name]))
    return diff


def _requirement(name, version):
    return f"{name} {version}" if version.startswith("@") else f"{name}=={version}"


def format_diff(diff):
    lines = [f"+ {_requirement(n, v)}" for n, v in diff["added"]]
    lines += [f"- {_requirement(n, v)}" for n, v in diff["removed"]]
    for key, mark in (("upgraded", "^"), ("downgraded", "v"), ("changed", "~")):
        lines += [f"{mark} {n} {a} -> {b}" for n, a, b in diff[key]]
    return lines or ["no changes"]
