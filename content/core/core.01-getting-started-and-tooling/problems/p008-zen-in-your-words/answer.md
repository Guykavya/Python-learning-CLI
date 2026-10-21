**1. Errors and guessing.** `"Marks: " + 87` raises
`TypeError: can only concatenate str (not "int") to str`. Python could have
guessed (turn 87 into text, or try to turn "Marks: " into a number), but either
guess could be wrong and the program would continue with a hidden bug. A loud,
immediate error with a line number is easier to fix than a wrong answer found
weeks later. The fix states the intent: `"Marks: " + str(87)` or
`print("Marks:", 87)`.

**2. Readability.** Rewritten:

```python
student_name = "Asha"
marks = 87
```

Rules applied: snake_case variable names; one statement per line (no `;`);
spaces around `=`; descriptive names instead of single letters like `m`.
Code is read far more often than it is written, so these choices save time.

**3. Explicit.** `import platform` followed by `platform.system()` shows where
`system` comes from. Using `os.environ.get("NAME", "default")` states the
default openly instead of relying on hidden behaviour.

**4. import twice.** Printed once. A module's top-level code runs only on its
first import in a process. The second `import this` finds the module already
loaded in `sys.modules` and does nothing.

Key ideas to check: TypeError instead of guessing; errors visible early;
snake_case, one statement per line, spaces around `=`, meaningful names;
explicit imports show origin; modules run once per process (sys.modules cache).
