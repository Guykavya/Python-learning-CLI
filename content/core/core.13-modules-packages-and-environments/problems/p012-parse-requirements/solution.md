## Approach

Clean the line step by step, in the order of the rules, so each step works on simpler text:

1. `partition("#")[0]` keeps the part before the first `#`.
2. `strip()`, then skip empty lines and lines that start with `-`.
3. `partition(";")[0]` drops the environment marker.
4. Walk over the name characters with an index. Everything before the index is the name, everything
   after is "extras + specifier".
5. Drop `[...]` if it comes first, then remove all spaces from the specifier.

pip normalises names because `Flask`, `flask` and `FLASK` are the same project on PyPI, and so are
`python_dateutil`, `python.dateutil` and `python-dateutil`. Comparing normalised names avoids
"duplicate" packages that are really one.

## Code

```python
def normalise_name(name):
    return name.lower().replace("_", "-").replace(".", "-")


def parse_requirements(path):
    result = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.partition("#")[0].strip()
            if not line or line.startswith("-"):
                continue
            line = line.partition(";")[0].strip()
            i = 0
            while i < len(line) and (line[i].isalnum() or line[i] in "-_."):
                i += 1
            name = normalise_name(line[:i])
            rest = line[i:].strip()
            if rest.startswith("["):
                rest = rest.partition("]")[2]
            spec = rest.replace(" ", "").replace("\t", "")
            result.append((name, spec))
    return result
```

## Complexity

O(total length of the file): every character is looked at a constant number of times.

## Another way

The `packaging` library (which pip itself uses) has `packaging.requirements.Requirement(line)`. It
handles every corner of the format: URLs, markers, extras, and the exact name rules. Use it in real
projects; writing the small parser yourself shows what a specifier really is. A regular expression like
`^([A-Za-z0-9._-]+)` can also find the name.
