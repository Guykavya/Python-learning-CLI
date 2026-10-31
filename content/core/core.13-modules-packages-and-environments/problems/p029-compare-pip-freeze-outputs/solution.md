## Approach

Parse first, compare second. Parsing normalises names (so `Flask` and `flask` match) and keeps the
version text unchanged for printing. Comparing walks over the union of both name sets in sorted
order. For versions, turn `"1.26.18"` into the tuple `(1, 26, 18)` and drop trailing zeros, so tuples
compare like versions; anything that is not only numbers and dots cannot be ordered safely and is
reported as "changed".

## Code

```python
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
```

## Complexity

O((n + m) log(n + m)) for n and m packages: parsing is linear, sorting the union dominates.

## Another way

With the `re` module, `normalise` is one line: `re.sub(r"[-_.]+", "-", name).lower()` (this is the
exact rule written in PEP 503). For real version comparison, including `rc`, `post` and `dev`
releases, the `packaging` library (installed with pip) has `packaging.version.Version`, which
implements PEP 440 completely: `Version("2.0rc1") < Version("2.0")` is `True`.
