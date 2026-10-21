The model answer is shown when you check. Ideas that must appear:

1. Language = rules; CPython = the reference interpreter; PyPy (JIT) or MicroPython.
2. Source is compiled to bytecode, then the evaluation loop executes it.
3. SyntaxError stops everything at compile time; NameError happens only when
   the line runs.
4. `.pyc` files in `__pycache__` cache bytecode for imports; safe to delete; ignore in Git.
5. major.minor.micro; new features are not available in older versions.
