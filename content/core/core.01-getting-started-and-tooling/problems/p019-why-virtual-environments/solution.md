The model answer is shown when you check. Ideas that must appear:

1. Per-project isolation of packages and versions; system Python is protected (PEP 668).
2. `python3 -m venv .venv`, `source .venv/bin/activate`, `python -m pip install`,
   `pip freeze > requirements.txt`.
3. `pyvenv.cfg`, a link to the base interpreter, its own `site-packages`;
   activation only edits `PATH` and the prompt.
4. `python -m pip` installs into the interpreter you actually run.
5. Do not commit `.venv`; commit `requirements.txt`; ignore `.venv/`.
6. Mismatched interpreters; check with `which`, `sys.executable`, `pip --version`.
