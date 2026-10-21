**1. The problem.** Without venvs every project shares one set of installed
packages. If project A needs `requests` 2.28 and project B needs 2.32, installing
one breaks the other. Modern Linux also blocks `pip install` into the system
Python (PEP 668, "externally-managed-environment") to protect OS tools. A venv
gives each project its own private package folder.

**2. Commands.**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install requests
python -m pip freeze > requirements.txt
python app.py
```

**3. Inside.** `pyvenv.cfg` (records the base Python, its version, and whether
system packages are visible), `bin/python` (a link to the base interpreter, not
a copy), `bin/pip` and `activate` scripts, and `lib/python3.X/site-packages`
where packages are installed. When Python starts and finds `pyvenv.cfg`, it sets
`sys.prefix` to the venv and uses its `site-packages`. `activate` only puts
`.venv/bin` at the front of `PATH` and changes the prompt. So running
`.venv/bin/python app.py` directly works the same without activating.

**4. `python -m pip`.** It runs pip *with the same interpreter* that `python`
runs, so packages land where that Python looks. A bare `pip` might belong to a
different Python found earlier on `PATH`.

**5. Git.** No. `.venv` is large, contains absolute paths, and is
machine-specific. Commit `requirements.txt` and add `.venv/` to `.gitignore`.
Others rebuild with `python -m pip install -r requirements.txt`.

**6. ModuleNotFoundError.** Cause A: pip installed into one Python and `python3`
runs another (for example, the venv is not activated in this terminal, or `pip`
belongs to a different install). Cause B: the package went into a different venv,
or VS Code uses another interpreter. Check with `which python3`,
`python3 -m pip --version` (shows where pip installs),
`python3 -c "import sys; print(sys.executable, sys.prefix)"`, and
`python3 -m pip list`. Fix: activate the right venv and use `python -m pip install requests`.

Key ideas to check: isolation per project with an example; PEP 668; correct
commands including `-m venv` and `freeze`; venv links to base Python;
`site-packages`; `pyvenv.cfg`; activation only edits `PATH`; `python -m pip`
ties pip to the interpreter; never commit `.venv`, commit `requirements.txt`;
diagnose with `which`, `sys.executable`, `pip --version`.
