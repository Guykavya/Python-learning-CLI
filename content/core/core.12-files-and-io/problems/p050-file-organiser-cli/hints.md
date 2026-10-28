## Hint 1

Do not write one long `main`. Which small parts can you test alone? For example: "which folder does this file go to"
(`folder_for`), "which free name does it get" (`unique_target`), and "what is the full list of moves" (`plan_moves`).
Why is it useful to make the **whole plan first** and only then move files?

## Hint 2

```
parser: source, --by choices=[type,date,size] default type, --dest, --dry-run store_true
check source is a dir (else error, return 2); check dest (else error, return 2)
plan = []; reserved = set()
for path in sorted top-level files that are files and not hidden:
    target = free name in dest/folder_for(path) that is neither on disk nor in reserved
    reserved.add(target); plan.append((path, target))
if no plan: print "nothing to do"; return 0
for (path, target) in plan:
    if not dry run: mkdir parents, shutil.move (catch OSError -> message, count failed, continue)
    print verb + name + " -> " + target relative to dest
print summary; return 1 if failed else 0
```

## Hint 3

Free name: `n = 0; while target.exists() or target in reserved: n += 1; target = folder / f"{stem}_{n}{suffix}"`.
Dry run and real run must call the same planning function. Only the part that touches the disk is skipped.
Date folder: `datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m")`.
