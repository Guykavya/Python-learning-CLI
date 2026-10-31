# Find and classify the imports of a source file

Before you write a `requirements.txt` or the `dependencies` of a `pyproject.toml`, you need to know
which packages your code really imports. Some are in the **standard library** (they come with Python),
some are **local** (your own modules), and the rest are **third party** (they must be installed with
pip).

Write two functions in `solution.py`. Both receive the **source code** of a file as a string.

### `find_imports(source)`

Return a sorted list, without duplicates, of the **top-level** names of all *absolute* imports
anywhere in the code, also inside functions:

- `import os.path` -> `os`
- `import numpy as np` -> `numpy`
- `from collections.abc import Iterable` -> `collections`
- `import a, b` -> `a` and `b`
- relative imports (`from . import x`, `from .utils import y`) are **not** included here.

### `classify_imports(source, local=())`

Return a dict with exactly three keys, `"stdlib"`, `"third_party"` and `"local"`, each a sorted
list without duplicates:

- a top-level name that is in `local` (the names of your own modules) is **local**, even if the
  standard library has a module with the same name (your file would shadow it);
- otherwise a name in `sys.stdlib_module_names` is **stdlib**;
- otherwise it is **third_party**;
- every relative import is **local**, written as dots plus the module part exactly as in the code:
  `from .utils import y` -> `".utils"`, `from ..core.db import q` -> `"..core.db"`,
  `from . import x` -> `"."`.

A source with a syntax error raises `SyntaxError` (just let it happen).

### The tool: `ast`

Searching the text for the word `import` breaks on strings, comments and `import a, b`. The
`ast` module parses Python source into a tree of nodes, exactly like Python itself does:

```python
import ast

tree = ast.parse("import os.path as p\nfrom ..core import db\n")
for node in ast.walk(tree):          # every node in the tree, also inside functions
    if isinstance(node, ast.Import):
        print([alias.name for alias in node.names])   # ['os.path']
    elif isinstance(node, ast.ImportFrom):
        print(node.module, node.level)                # core 2
```

For `ast.ImportFrom`, `node.level` is the number of leading dots (0 for an absolute import) and
`node.module` is the text after the dots, or `None` for `from . import x`.

## Example

```python
>>> src = '''
... import os, sys
... import numpy as np
... from collections.abc import Iterable
... from .helpers import tidy
... import config
...
... def load():
...     import requests.adapters
...     text = "import fake"    # a string, not an import
... '''
>>> find_imports(src)
['collections', 'config', 'numpy', 'os', 'requests', 'sys']
>>> classify_imports(src, local={"config"})
{'stdlib': ['collections', 'os', 'sys'], 'third_party': ['numpy', 'requests'], 'local': ['.helpers', 'config']}
```
