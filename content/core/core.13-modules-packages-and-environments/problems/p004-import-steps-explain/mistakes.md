- Saying `import` only "reads the functions". It runs every top-level line of the file.
- Saying the second import runs the file again but "nothing changes". It does not run at all; the module
  comes from `sys.modules`.
- Saying `__name__` is the file name `temps.py`. It is the module name `temps`, or `__main__` when started.
- Putting the `def` inside the `if __name__ == "__main__":` block. Then importers cannot use the function.
- Leaving out the search order: the script's own folder comes first in `sys.path`, which is also why a
  file named like a standard module (for example `random.py`) hides the real one.
