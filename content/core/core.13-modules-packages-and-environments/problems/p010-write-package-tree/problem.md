# Write a package tree with `__init__` files

A folder becomes a **regular package** when it has an `__init__.py` file. A package inside a package is
a **subpackage**, and it needs its own `__init__.py` too. Forgetting one is a classic source of confusing
import errors.

Write `write_package(root, files)` in `solution.py`.

- `root` is a folder (`str` or `Path`) that already exists.
- `files` is a dict: relative path (with `/`) → source text, for example
  `{"mathkit/stats/mean.py": "def mean(xs): ..."}`.
- Write every file under `root` (UTF-8), creating the folders it needs.
- Every folder **below** `root` that holds one of the files, and every folder between `root` and it,
  must get an `__init__.py`. If `files` does not give one for that folder, write an **empty** one.
  If `files` gives one, keep its text. Do not put an `__init__.py` in `root` itself.
- Return a **sorted list** of the relative paths of all files written (as `/` strings), including the
  added `__init__.py` files.

**Example**

```python
write_package("work", {
    "mathkit/__init__.py": "from .basic import add\n",
    "mathkit/basic.py": "def add(a, b):\n    return a + b\n",
    "mathkit/stats/mean.py": "def mean(xs):\n    return sum(xs) / len(xs)\n",
    "main.py": "import mathkit\n",
})
```

returns

```python
['main.py', 'mathkit/__init__.py', 'mathkit/basic.py', 'mathkit/stats/__init__.py', 'mathkit/stats/mean.py']
```

`mathkit/stats/__init__.py` was added (empty). `mathkit/__init__.py` keeps its own text. `main.py` sits in
`root`, so `root` gets no `__init__.py`. With `work` on `sys.path`, `from mathkit.stats.mean import mean` now works.
