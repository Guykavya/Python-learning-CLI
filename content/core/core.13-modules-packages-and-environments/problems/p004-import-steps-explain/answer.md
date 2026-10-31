**1. The first import.** Python first checks `sys.modules`, a dictionary of every module already loaded.
`"temps"` is not there. So Python searches the folders in `sys.path` in order. The first entry is the
folder of the script you started, so it finds `temps.py` there. It creates a new, empty **module object**,
sets `__name__ = "temps"` and `__file__`, and stores it in `sys.modules["temps"]` **before** running the
file. Then it runs `temps.py` from top to bottom, in the module's own namespace: the `def` creates
`c_to_f`, and the `print` line prints the demo. An `import` is real code execution, not "copy the
functions". Last, it binds the name `temps` in `report.py` to the module object.

**2. The second import.** Python checks `sys.modules` again, finds `"temps"`, and just binds the name to
the cached object. It does not search and does not run the file. That is why the demo appears once. Every
later import in any file of the program gets this same object. Only `importlib.reload` runs a file again.

**3. `__name__`.** When `temps.py` is imported, `__name__` is `"temps"`. When you run `python temps.py`,
that file is the main program, and Python sets its `__name__` to `"__main__"`.

**4. The guard.**

```python
# temps.py
def c_to_f(c):
    return c * 9 / 5 + 32


if __name__ == "__main__":
    print("Demo:", c_to_f(100))
```

On import the condition is false, so only the function is defined. Run directly, the demo runs.

**5. Why it matters.** Test files and other programs import your module only to use its functions. Code
at the top level runs on every import: a demo prints junk, a script that asks for `input()` freezes the
tests, and a slow job (reading a big file, a network call, deleting files) runs when nobody asked. The
guard lets one file be both a reusable module and a runnable script.
