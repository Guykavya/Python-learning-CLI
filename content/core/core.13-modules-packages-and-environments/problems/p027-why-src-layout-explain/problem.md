# Explain: why the src layout prevents testing the wrong copy

Meera packages her `notes_app`. She uses the **flat layout**:

```text
notes-project/
├── pyproject.toml
├── notes_app/
│   ├── __init__.py
│   └── storage.py
└── tests/
    └── test_storage.py
```

She builds a wheel and installs it into a fresh virtual environment with `pip install .`
(a normal, not editable, install). Then she runs `python -m pytest` from `notes-project/`. All tests
pass. She uploads the package. Users report at once: `ModuleNotFoundError: No module named
'notes_app.storage'`. Her `pyproject.toml` package list had a mistake, so the wheel only contained
`notes_app/__init__.py`.

Her friend says: "Use the **src layout**. Then your tests would have failed too."

```text
notes-project/
├── pyproject.toml
├── src/
│   └── notes_app/
│       ├── __init__.py
│       └── storage.py
└── tests/
    └── test_storage.py
```

In `answer.md` (about 200 to 350 words), explain:

1. Why the tests passed in the flat layout although the installed package was broken. Talk about
   `sys.path`: what `python -m pytest` (and `python` in general) puts at the front of it, and which copy
   of `notes_app` the tests therefore imported.
2. Why the same mistake makes the tests **fail** with the src layout. Which `notes_app` can the tests
   find now?
3. One more problem of the flat layout: what can go wrong when your project folder contains a module
   whose name matches an installed or standard-library module?
4. What an **editable install** (`pip install -e .`) does, and why it is the usual way to work on a
   src-layout project day to day.
5. A short rule Meera can remember.

## Example of the level of detail

"`python -m` puts the current working directory at the front of `sys.path`. So `import notes_app`
finds the folder `notes-project/notes_app/` before it looks at `site-packages`." A good answer goes
on like this.
