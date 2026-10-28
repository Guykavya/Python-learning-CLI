## Hint 1

Who installs a library, and who installs an application? A library lives in other people's
environments next to other libraries. An application is the top of the tree: nobody installs
something on top of it. Which of the two needs flexibility, and which needs the exact same packages
every time?

## Hint 2

Answer in order: (1) range = flexible, pin = exact; (2) unpinned transitive dependency + resolver
picks the newest on each install; (3) two libraries with different exact pins cannot be installed
together; (4) lock file = every package, exact version, hashes, installs the same set again; (5) ranges
in `pyproject.toml`, lock file for the app, upgrade by re-locking and testing.
