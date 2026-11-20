## Hint 1

Split the work in two: (a) turn each pattern into a small record (negated? directories only? anchored?) and a regular expression; (b) for a path, find the **last** pattern that matches.

## Hint 2

Glob to regex, character by character: `**/` becomes `(?:.*/)?`, a final `/**` becomes `/.*`, `*` becomes `[^/]*`, `?` becomes `[^/]`, everything else goes through `re.escape`. A non-anchored pattern is matched against the **last component** of the path only.

## Hint 3

Rule 8: before judging the path itself, judge each parent directory (`a`, `a/b`, ... as directories). If any is ignored, return `True`.

```text
for each proper prefix directory d of the path (shallowest first):
    if verdict(d, is_dir=True): return True
return verdict(path, is_dir)
verdict: ignored = False; for rules in order: if rule matches: ignored = not rule.negated
```
