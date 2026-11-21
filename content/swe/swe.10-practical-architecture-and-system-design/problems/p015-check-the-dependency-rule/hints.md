## Hint 1

Split the job into two small functions: one that **reads a source text and returns what it imports** (project modules and external libraries), and one that **applies the rule** to those sets. For the first, `ast.walk` visits every node of the tree, including imports hidden inside functions. Which two node types are imports, and which attribute tells you the dots of a relative import?

## Hint 2

```text
ast.Import:      names like "taskboard.repo" or "sqlite3": first part == package -> project module = second part; else external = first part
ast.ImportFrom:  level >= 1 (relative): module -> its first part; no module -> every imported name is a module ("from . import repo")
                 level == 0: first part == package -> module part 2, or (no part 2) every imported name; else external = first part
rule: project module in layers and rank(its layer) > rank(my layer) -> violation (me, it);  external in EXTERNAL_BANS[my layer] -> violation (me, library)
return sorted(set of pairs)
```
