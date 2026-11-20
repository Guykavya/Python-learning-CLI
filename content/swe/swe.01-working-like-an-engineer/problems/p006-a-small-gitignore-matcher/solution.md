## Approach

```python
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
```

**Why a record per pattern:** `negated`, `dir_only` and `anchored` are read off the pattern text once; then every path is judged by the same short loop. **Why last match wins:** git evaluates patterns in order and a later rule overrides an earlier one, which is how `!keep.pyc` can follow `*.pyc`.

**Why the parent loop:** git never even looks inside an ignored directory, so a `!` rule for a file inside it has no effect. Checking each parent first reproduces this. For `docs/build/index.html` and the pattern `build/`: the parent `docs` is not ignored, the parent `docs/build` is (a directory named `build`), so the answer is `True`.

Example with `["logs/*", "!logs/keep.txt"]`: for `logs/keep.txt`, no parent is ignored (`logs` itself is not matched, since `logs/*` matches only things inside it); the file matches `logs/*` (ignored) and then `!logs/keep.txt` (re-included): the answer is `False`.

## Complexity

`O(depth * patterns)` per path.

## Another way

Run `git check-ignore -v path` in a real repository (chapter section 4.3): it names the rule that decided. This problem rebuilds that decision so you understand it.
