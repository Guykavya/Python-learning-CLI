- Searching the text with `"import" in line`. Comments, strings and docstrings give false hits, and
  `import a, b` gives only one.
- Looping over `tree.body` only. That misses imports inside functions, `if` and `try` blocks.
- Using `node.module` for `from . import x`. It is `None`; `None.split` crashes.
- Keeping the full dotted name (`os.path`) instead of the top-level name (`os`).
- Checking stdlib before local. A local `random.py` shadows the real `random`, so it is local.
- Returning only the keys that have names. The result always has all three keys.
