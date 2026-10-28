## Hint 1

When two copies of `notes_app` exist (the folder in the project and the one in `site-packages`),
which one does `import notes_app` load? Python walks `sys.path` from the front. What is at the front
when you run `python -m pytest` from the project folder?

## Hint 2

Answer in order: (1) current folder first on `sys.path` -> source copy found, installed copy ignored;
(2) with `src/`, the project folder has no `notes_app`, so only the installed one can be imported;
(3) files in the project root can shadow real modules; (4) `-e` links `site-packages` to `src/`, so
edits are live but imports go the installed way; (5) one-sentence rule.
