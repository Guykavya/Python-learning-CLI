# A tiny linter

Linters like `ruff` and `flake8` do not run your code. They **parse** it into a tree (an
abstract syntax tree, AST) and look for shapes in the tree that are almost always mistakes. The
standard library can do the parsing: `ast.parse(source)` returns the tree, and `ast.walk(tree)`
visits every node in it.

Write `find_issues(source: str) -> list[tuple[int, str]]` in `solution.py` that reports three of
ruff's rules, as `(line_number, code)` pairs **sorted** by line number, then by code:

| Code | Rule | What to report |
|---|---|---|
| `F401` | unused import | each name bound by `import ...` or `from ... import ...` that never appears as a name being **read** (`ast.Name` with `ast.Load` context) anywhere in the module. Report it at the line of the import statement, once per unused name. |
| `E722` | bare except | each `except:` with no exception type (`ast.ExceptHandler` whose `type` is `None`), at the line of the `except`. |
| `B006` | mutable default argument | each default value of a function or lambda parameter (including keyword-only ones) that is a list, dict or set **literal** (`[]`, `{}`, `{1}`), or a call `list()`, `dict()` or `set()`. Report the line of the default value. |

Details for F401:

- `import os.path` binds the name `os`; `import numpy as np` binds `np`;
  `from a import b as c` binds `c`.
- `os.path.join(...)` counts as using `os` (the tree contains a `Name` node `os`).
- Ignore `from __future__ import ...` and `from x import *`.

If the source has a syntax error, return `[(line_of_the_error, "E999")]` (use the exception's
`lineno`).

**Example**

```python
source = '''\
import os
import sys, json
from typing import Any as A

def load(path, cache={}, *, seen=list()):
    try:
        return json.loads(open(path).read())
    except:
        return None
'''
find_issues(source)
# [(1, 'F401'), (2, 'F401'), (3, 'F401'), (5, 'B006'), (5, 'B006'), (8, 'E722')]
```

`os`, `sys` and `A` are never read; `json` is. Line 5 has two mutable defaults.
