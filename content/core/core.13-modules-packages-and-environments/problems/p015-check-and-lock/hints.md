## Hint 1

First build a new dict from `installed` with normalised names, so `"Flask"` becomes `"flask"`. Then every
lookup is a simple `name in versions`. What do you need to remember about a name that failed once, so
that a later passing line for the same name does not lock it?

## Hint 2

Keep a set `failed` of names with at least one problem. Add every required, installed name to a set
`seen`. At the end, the lock is every name in `seen` that is not in `failed`, sorted.

## Hint 3

```
versions = {normalise(n): v for n, v in installed.items()}
problems, failed, ok = [], set(), set()
for name, spec in requirements:
    if name not in versions:
        problems.append(f"{name}: not installed"); failed.add(name)
    elif not satisfies(versions[name], spec):
        problems.append(f"{name}: {versions[name]} does not satisfy {spec}"); failed.add(name)
    else:
        ok.add(name)
lock = [f"{n}=={versions[n]}" for n in sorted(ok - failed)]
return lock, problems
```
