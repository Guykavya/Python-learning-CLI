- Saying the src layout is "just tidier". Its real job is to make the import system find only the
  installed package.
- Thinking `pip install .` makes `import notes_app` use the installed copy. A folder of the same name
  earlier on `sys.path` still wins.
- Forgetting that `python -m ...` and plain `python` (from the project folder) put that folder on
  `sys.path`.
- Saying an editable install copies the files. It links back to `src/`, which is why edits are live.
- Thinking the src layout means you must reinstall after every edit. That is what `-e` is for.
