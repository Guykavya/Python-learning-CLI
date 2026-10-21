- `print("Hello,", name, "!")` puts a space before the `!` (`Hello, Asha !`).
- Using `os.environ["LEARNER_NAME"]`: crashes with `KeyError` when unset.
- Setting the variable in bash without `export` and wondering why Python sees
  the default. Only exported variables reach child processes.
- Forgetting `import os`: `NameError: name 'os' is not defined`.
