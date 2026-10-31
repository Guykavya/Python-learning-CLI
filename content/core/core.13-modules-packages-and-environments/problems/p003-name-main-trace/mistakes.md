- Thinking `__name__` is always the file name. It is `"__main__"` for the file you start.
- Printing `tools running as a script` in command 1. `tools` is imported there, so its `if` is false.
- Forgetting that the top-level `print` in `tools.py` still runs on import. Only the code inside the
  `if` block is protected.
- Printing `app running as a script` in command 3. `app` is imported by the `-c` string, so its
  `__name__` is `app`.
