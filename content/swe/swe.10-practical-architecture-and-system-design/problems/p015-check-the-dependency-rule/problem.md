# Check the dependency rule

Chapter section 10.2 (the dependency rule) and "Try it: draw the line". The finished shape of Taskboard has layers, and arrows that mean "imports" point **inwards**, towards the domain:

```text
                      main.py          composition root + HTTP translation        (web)
                     services, dispatch                                    (services)
      uow, repo, db, mailer, notifications: SQLite and e-mail                      (infrastructure)
                  domain.py, errors.py   import nothing else                      (domain)
```

A rule that is not enforced decays: someone breaks it on a busy Friday ("a quick fix imports `sqlite3` into the services"). Because Python has `ast`, you can make the rule a **test** that fails in CI. Write the checker.

## What to write

`LAYER_RANK` and `EXTERNAL_BANS` are given in the starter:

```python
LAYER_RANK = {"domain": 0, "services": 1, "infrastructure": 2, "web": 3}
EXTERNAL_BANS = {"domain": {"sqlite3", "fastapi", "httpx", "requests", "smtplib"},
                 "services": {"sqlite3", "fastapi", "httpx", "requests", "smtplib"}}

def violations(sources: dict[str, str], layers: dict[str, str], package: str = "taskboard") -> list[tuple[str, str]]: ...
```

- `sources` maps a **module name** (`"services"`) to its **source text**. `layers` maps each project module name to its layer (`"services"` -> `"services"`, `"repo"` -> `"infrastructure"`, ...). A module in `sources` that is not in `layers` raises `ValueError`.
- Parse each source with `ast` and find **every** import, also inside functions. Work out which **project module** it imports:
  - relative: `from .repo import X` -> `repo`; `from . import repo, errors` -> `repo` and `errors`;
  - absolute with the package name: `from taskboard.repo import X` -> `repo`; `from taskboard import repo` -> `repo`; `import taskboard.repo` -> `repo`;
  - anything else is an **external** library, identified by its top-level name (`import sqlite3` -> `sqlite3`; `from fastapi.responses import X` -> `fastapi`).
- The rule: a module may import project modules of its **own layer or an inner (lower-rank) layer**. Importing a module of a **higher-rank** layer is a violation `(module, imported_module)`. A project module that is not in `layers` is ignored. Importing an external library listed in `EXTERNAL_BANS` for the module's layer is a violation `(module, library)`.
- Return the violations as a **sorted** list of unique `(module, imported)` pairs.

## Example

```python
layers = {"errors": "domain", "domain": "domain", "services": "services", "repo": "infrastructure", "main": "web"}
violations({"services": "import sqlite3\nfrom .repo import SqliteTaskRepo\nfrom .domain import Task"}, layers)
# [('services', 'repo'), ('services', 'sqlite3')]
violations({"main": "from . import services, repo\nfrom fastapi import FastAPI"}, layers)
# []    (the web layer may import everything inside it, and fastapi is its business)
```

Why this is worth a test (chapter 10.2): **the test turns a design principle into something that fails in CI**, which is the only way principles survive. The chapter's own `ast` test walks the files of `taskboard/`; here the sources come in as a dictionary so that the rule can be tested on examples.
