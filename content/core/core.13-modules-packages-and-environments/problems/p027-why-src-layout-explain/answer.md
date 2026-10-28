**1. Why the flat layout lied.** `python -m pytest` puts the current folder, `notes-project/`, at the
front of `sys.path` (pytest's default import mode also inserts the test folder's base). Python takes
the **first** match on `sys.path`. So `import notes_app` found the source folder
`notes-project/notes_app/`, which has `storage.py`, and never looked at the installed copy in
`site-packages`. The tests checked the source tree, not the package users get. The broken wheel was
never tested.

**2. Why src layout catches it.** With the code inside `src/`, the project folder no longer contains a
`notes_app` folder. `src/` is not on `sys.path` unless you add it. The only `notes_app` the tests can
import is the **installed** one. Since that wheel lacks `storage.py`, `import notes_app.storage` fails
in the tests too, before any user sees it. The layout forces "install, then test what was installed".

**3. Shadowing.** In the flat layout everything at the top of the project is importable just because
you stand in that folder. A helper file `json.py`, `logging.py` or `requests.py` there shadows the real
module for every import while you work, and can produce errors that never happen for users (or the
other way round). Scripts in the project root can also import modules that are not part of the
package at all, and then break after installation.

**4. Editable installs.** `pip install -e .` (or `uv pip install -e .`) installs the project so that
`site-packages` points back at `src/notes_app` instead of copying it. Changes in the source are live
without reinstalling, and imports still go through the normal installed route, so metadata, entry
points and `python -m notes_app` work like for a user. For a final check, build the wheel and install it
normally in a fresh venv.

**5. Rule.** "Code in `src/`, install it, then test. If the tests can import it, so can users."
