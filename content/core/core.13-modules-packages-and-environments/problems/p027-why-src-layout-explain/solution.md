## Approach

Everything follows from one fact: Python imports the first match on `sys.path`, and running Python
from a folder puts that folder at the front. The flat layout makes the source copy win; the src
layout removes it from the search, so the installed copy is the one tested.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Prove it to yourself: in a flat-layout project, print `notes_app.__file__` inside a test. It shows the
project folder, not `site-packages`. In the src layout, after `pip install .`, the same print shows
`.../site-packages/notes_app/__init__.py`. Problem p030 builds a real src-layout project.
